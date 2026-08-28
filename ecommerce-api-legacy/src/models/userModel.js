const { get, run } = require("../lib/database");

function findByEmail(db, email) {
  return get(db, "SELECT id FROM users WHERE email = ?", [email]);
}

function create(db, name, email, hashedPassword) {
  return run(db, "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, hashedPassword]);
}

function deleteById(db, userId) {
  return run(db, "DELETE FROM users WHERE id = ?", [userId]);
}

module.exports = { findByEmail, create, deleteById };
