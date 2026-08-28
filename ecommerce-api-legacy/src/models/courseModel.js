const { get, all } = require("../lib/database");

function findActiveById(db, courseId) {
  return get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
}

function findAll(db) {
  return all(db, "SELECT * FROM courses");
}

function getFinancialReport(db) {
  const sql = `
    SELECT
      c.id   AS courseId,
      c.title AS courseTitle,
      u.name  AS studentName,
      p.amount AS paidAmount,
      p.status AS paymentStatus
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u       ON u.id = e.user_id
    LEFT JOIN payments p    ON p.enrollment_id = e.id
    ORDER BY c.id
  `;
  return all(db, sql);
}

module.exports = { findActiveById, findAll, getFinancialReport };
