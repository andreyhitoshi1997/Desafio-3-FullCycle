const { Router } = require("express");
const { requireAdminToken } = require("../middlewares/adminAuth");
const { buildDeleteUserHandler } = require("../controllers/userController");

function createUserRoutes(db) {
  const router = Router();
  router.delete("/api/users/:id", requireAdminToken, buildDeleteUserHandler(db));
  return router;
}

module.exports = { createUserRoutes };
