const express = require("express");
const config = require("./config/settings");
const logger = require("./lib/logger");
const { createDatabase } = require("./lib/database");
const { initializeSchema, seedData } = require("./lib/seed");
const { createCheckoutRoutes } = require("./routes/checkoutRoutes");
const { createAdminRoutes } = require("./routes/adminRoutes");
const { createUserRoutes } = require("./routes/userRoutes");
const { errorHandler } = require("./middlewares/errorHandler");
const { createSimulatedGateway } = require("./services/payment/simulatedGateway");
const { createPaymentService } = require("./services/payment/paymentService");

async function bootstrap() {
  const db = createDatabase(config.dbPath);

  await initializeSchema(db);
  await seedData(db);

  const gateway = createSimulatedGateway({ gatewayKey: config.paymentGatewayKey });
  const paymentService = createPaymentService({ gateway });

  const app = express();
  app.use(express.json());

  app.use(createCheckoutRoutes(db, paymentService));
  app.use(createAdminRoutes(db));
  app.use(createUserRoutes(db));

  app.use(errorHandler);

  app.listen(config.port, () => {
    logger.info("Frankenstein LMS started", { port: config.port });
  });
}

bootstrap().catch((err) => {
  logger.error("Failed to start application", { message: err.message });
  process.exit(1);
});
