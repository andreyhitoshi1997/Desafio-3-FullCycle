const bcrypt = require("bcryptjs");
const config = require("../config/settings");
const logger = require("../lib/logger");
const courseModel = require("../models/courseModel");
const userModel = require("../models/userModel");
const enrollmentModel = require("../models/enrollmentModel");
const paymentModel = require("../models/paymentModel");
const auditLogModel = require("../models/auditLogModel");
const paymentService = require("../services/paymentService");

function buildCheckoutHandler(db) {
  return async function checkout(req, res, next) {
    try {
      const { userName, email, password, courseId, cardNumber } = parseCheckoutBody(req.body);

      if (!userName || !email || !courseId || !cardNumber) {
        return res.status(400).send("Bad Request");
      }

      const course = await courseModel.findActiveById(db, courseId);
      if (!course) return res.status(404).send("Curso não encontrado");

      const userId = await findOrCreateUser(db, userName, email, password);

      const paymentStatus = paymentService.processPayment(cardNumber, config.paymentGatewayKey);
      if (paymentStatus === "DENIED") return res.status(400).send("Pagamento recusado");

      const { lastID: enrollmentId } = await enrollmentModel.create(db, userId, courseId);
      await paymentModel.create(db, enrollmentId, course.price, paymentStatus);
      await auditLogModel.create(db, `Checkout curso ${courseId} por ${userId}`);

      logger.info("Checkout completed", { userId, courseId, enrollmentId });

      return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
    } catch (err) {
      next(err);
    }
  };
}

function parseCheckoutBody(body) {
  return {
    userName: body.usr,
    email: body.eml,
    password: body.pwd,
    courseId: body.c_id,
    cardNumber: body.card,
  };
}

async function findOrCreateUser(db, userName, email, password) {
  const existingUser = await userModel.findByEmail(db, email);
  if (existingUser) return existingUser.id;

  const rawPassword = password || "123456";
  const hashedPassword = await bcrypt.hash(rawPassword, config.bcryptRounds);
  const { lastID: newUserId } = await userModel.create(db, userName, email, hashedPassword);
  return newUserId;
}

module.exports = { buildCheckoutHandler };
