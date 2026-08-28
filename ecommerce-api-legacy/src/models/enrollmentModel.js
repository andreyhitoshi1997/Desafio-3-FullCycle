const { run, all } = require("../lib/database");

function create(db, userId, courseId) {
  return run(db, "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, courseId]);
}

function findByUserId(db, userId) {
  return all(db, "SELECT id FROM enrollments WHERE user_id = ?", [userId]);
}

function deleteByUserId(db, userId) {
  return run(db, "DELETE FROM enrollments WHERE user_id = ?", [userId]);
}

module.exports = { create, findByUserId, deleteByUserId };
