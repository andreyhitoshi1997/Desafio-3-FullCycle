const config = require("../config/settings");

function requireAdminToken(req, res, next) {
  const token = req.headers["x-admin-token"];
  if (!token || token !== config.adminToken) {
    return res.status(401).json({ error: "Unauthorized: valid X-Admin-Token header required" });
  }
  next();
}

module.exports = { requireAdminToken };
