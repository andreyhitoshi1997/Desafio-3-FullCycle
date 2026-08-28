const logger = require("../lib/logger");
const userModel = require("../models/userModel");
const enrollmentModel = require("../models/enrollmentModel");
const paymentModel = require("../models/paymentModel");

function buildDeleteUserHandler(db) {
  return async function deleteUser(req, res, next) {
    try {
      const userId = req.params.id;

      const enrollments = await enrollmentModel.findByUserId(db, userId);
      const enrollmentIds = enrollments.map((enrollment) => enrollment.id);

      if (enrollmentIds.length > 0) {
        await paymentModel.deleteByEnrollmentIds(db, enrollmentIds);
      }
      await enrollmentModel.deleteByUserId(db, userId);
      await userModel.deleteById(db, userId);

      logger.info("User deleted with cascade", { userId, enrollmentsRemoved: enrollmentIds.length });

      return res.json({
        message: "User deleted",
        cascaded: { enrollments: enrollmentIds.length, payments: enrollmentIds.length },
      });
    } catch (err) {
      next(err);
    }
  };
}

module.exports = { buildDeleteUserHandler };
