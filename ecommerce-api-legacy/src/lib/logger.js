const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const currentLevel = LEVELS[process.env.LOG_LEVEL] || LEVELS.info;

function formatEntry(level, message, data) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
  };
  if (data !== undefined) entry.data = data;
  return JSON.stringify(entry);
}

function debug(message, data) {
  if (currentLevel <= LEVELS.debug) process.stdout.write(formatEntry("debug", message, data) + "\n");
}

function info(message, data) {
  if (currentLevel <= LEVELS.info) process.stdout.write(formatEntry("info", message, data) + "\n");
}

function warn(message, data) {
  if (currentLevel <= LEVELS.warn) process.stderr.write(formatEntry("warn", message, data) + "\n");
}

function error(message, data) {
  if (currentLevel <= LEVELS.error) process.stderr.write(formatEntry("error", message, data) + "\n");
}

module.exports = { debug, info, warn, error };
