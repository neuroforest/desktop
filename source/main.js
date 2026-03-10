#!/usr/bin/env node

/*
This script connects to a Neo4j database and populates
$tw.preloadTiddlers before the main TiddlyWiki boot process begins.
*/

// --- Neo4j Setup (Requires `npm install neo4j-driver`) ---
const neo4jDriver = require("neo4j-driver");

const currentWindow = nw.Window.get();
currentWindow.on('new-win-policy', (frame, url, policy) => {
	console.log("Opening new window.")
  policy.ignore();
  nw.Shell.openExternal(url);
});

// IMPORTANT: Replace these with your actual configuration details
const NEO4J_URI = process.env.NEO4J_URI;
const NEO4J_USER = process.env.NEO4J_USER;
const NEO4J_PASSWORD = process.env.NEO4J_PASSWORD;

const driver = neo4jDriver.driver(
  NEO4J_URI,
  neo4jDriver.auth.basic(NEO4J_USER, NEO4J_PASSWORD)
);

/**
 * Connects to Neo4j, retrieves all Tiddler nodes, and formats them
 * for TiddlyWiki's preload structure.
 * @returns {Array} Array of tiddler objects ready for $tw.preloadTiddlers.
 */
async function loadTiddlersFromNeo4j() {
  let session;
  try {
    await driver.verifyConnectivity();
    session = driver.session({ database: "neo4j" });

    console.log("Connected to Neo4j. Loading Tiddlers...");

    // Cypher to fetch all tiddlers and their properties
    const cypherQuery = `
      MATCH (t:Tiddler)
      RETURN properties(t) AS fields;
    `;

    const result = await session.run(cypherQuery);

    const preloadedTiddlers = result.records.map(record => {
      const fields = record.get("fields");
      delete fields.adaptorInfo;
      fields.created = new Date(fields.created);
      fields.modified = new Date(fields.modified);

      // TiddlyWiki expects an object with a 'fields' property for preload.
      return fields;
    });

    console.log(`Successfully loaded ${preloadedTiddlers.length} tiddlers from Neo4j.`);
    return preloadedTiddlers;
  } catch (error) {
    console.error("--- Neo4j Loading Error ---");
    console.error("Could not load tiddlers from database. Falling back to default boot process.");
    console.error(error.message);
    console.error("---------------------------");
    return [];
  } finally {
    if (session) {
      await session.close();
    }
  }
}

// Close the HTTP server before page reload so the port is free on restart
window.addEventListener("beforeunload", function() {
  if (global._nodeServer) {
    global._nodeServer.close();
  }
  if (global._neo4jDriver) {
    global._neo4jDriver.close();
  }
});

// Wrap the main boot process in an async function
(async () => {
  const port = process.env.PORT
  const args = (process.env.DESKTOP_ARGS || "").split(" ").filter(Boolean)
  // Intercept http.createServer to capture the server reference for cleanup
  global._neo4jDriver = driver;
  const http = require("http");
  const _origCreateServer = http.createServer.bind(http);
  http.createServer = function(...args) {
    const server = _origCreateServer(...args);
    global._nodeServer = server;
    return server;
  };
  var $tw = require("../tw5/boot/bootprefix.js").bootprefix()
  $tw.boot.argv = ["./tw5/editions/neuro-neo4j", "--listen", `port=${port}`, ...args];
  const preloadData = await loadTiddlersFromNeo4j();
  $tw.preloadTiddlers = preloadData;
  var $tw = require("../tw5/boot/boot.js").TiddlyWiki($tw);
  global.$tw = $tw;
  window.$tw = $tw;
})();