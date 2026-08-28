const { Router } = require("express");
const { requireAdminToken } = require("../middlewares/adminAuth");
const { buildFinancialReportHandler } = require("../controllers/financialReportController");

function createAdminRoutes(db) {
  const router = Router();
  router.get("/api/admin/financial-report", requireAdminToken, buildFinancialReportHandler(db));
  return router;
}

module.exports = { createAdminRoutes };
