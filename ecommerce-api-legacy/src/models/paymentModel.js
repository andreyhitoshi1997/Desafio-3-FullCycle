const { run } = require("../lib/database");

function create(db, enrollmentId, amount, status) {
  return run(
    db,
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [enrollmentId, amount, status],
  );
}

function deleteByEnrollmentIds(db, enrollmentIds) {
  if (enrollmentIds.length === 0) return Promise.resolve({ changes: 0 });
  const placeholders = enrollmentIds.map(() => "?").join(", ");
  return run(db, `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
}

module.exports = { create, deleteByEnrollmentIds };
