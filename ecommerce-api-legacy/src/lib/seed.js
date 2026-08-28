const { run } = require("./database");

const SCHEMA_STATEMENTS = [
  "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)",
  "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)",
  "CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)",
  "CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)",
  "CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)",
];

const SEED_STATEMENTS = [
  ["INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", ["Leonan", "leonan@fullcycle.com.br", "seeded"]],
  ["INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", ["Clean Architecture", 997.0, 1]],
  ["INSERT INTO courses (title, price, active) VALUES (?, ?, ?)", ["Docker", 497.0, 1]],
  ["INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]],
  ["INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [1, 997.0, "PAID"]],
];

async function initializeSchema(db) {
  for (const statement of SCHEMA_STATEMENTS) {
    await run(db, statement);
  }
}

async function seedData(db) {
  for (const [sql, params] of SEED_STATEMENTS) {
    await run(db, sql, params);
  }
}

module.exports = { initializeSchema, seedData };
