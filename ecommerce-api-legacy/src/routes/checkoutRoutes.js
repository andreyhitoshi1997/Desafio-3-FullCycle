const { Router } = require("express");
const { buildCheckoutHandler } = require("../controllers/checkoutController");

function createCheckoutRoutes(db, paymentService) {
  const router = Router();
  router.post("/api/checkout", buildCheckoutHandler(db, paymentService));
  return router;
}

module.exports = { createCheckoutRoutes };
