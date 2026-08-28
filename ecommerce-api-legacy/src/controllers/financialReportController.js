const courseModel = require("../models/courseModel");

function buildFinancialReportHandler(db) {
  return async function financialReport(_req, res, next) {
    try {
      const rows = await courseModel.getFinancialReport(db);
      const report = buildReportFromRows(rows);
      return res.json(report);
    } catch (err) {
      next(err);
    }
  };
}

function buildReportFromRows(rows) {
  const coursesMap = new Map();

  for (const row of rows) {
    if (!coursesMap.has(row.courseId)) {
      coursesMap.set(row.courseId, { course: row.courseTitle, revenue: 0, students: [] });
    }
    const courseData = coursesMap.get(row.courseId);

    if (!row.studentName) continue;

    const paidAmount = row.paidAmount || 0;
    if (row.paymentStatus === "PAID") {
      courseData.revenue += paidAmount;
    }
    courseData.students.push({ student: row.studentName, paid: paidAmount });
  }

  return Array.from(coursesMap.values());
}

module.exports = { buildFinancialReportHandler };
