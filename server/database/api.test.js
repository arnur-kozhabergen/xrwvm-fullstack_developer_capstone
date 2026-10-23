/* global fetch */
const { test, after, before } = require("node:test");
const assert = require("node:assert/strict");
const mongoose = require("mongoose");
process.env.BACKEND_WRITE_TOKEN = require("node:crypto")
  .randomBytes(32)
  .toString("hex");
process.env.PORT = "3099";
process.env.MONGO_URL =
  process.env.MONGO_URL || "mongodb://127.0.0.1:27017/fullstack_ci";
const { start } = require("./app");
let server;
before(async () => {
  server = await start();
});
after(async () => {
  if (server) await new Promise((resolve) => server.close(resolve));
  await mongoose.disconnect();
});
test("actual Mongo-backed endpoints and inserted review", async () => {
  const base = "http://127.0.0.1:3099";
  const all = await fetch(base + "/fetchDealers");
  assert.equal(all.status, 200);
  const dealers = await all.json();
  assert.ok(dealers.length > 0);
  const kansas = await (await fetch(base + "/fetchDealers/Kansas")).json();
  assert.ok(kansas.length > 0);
  assert.ok(kansas.every((x) => x.state === "Kansas"));
  const detail = await (
    await fetch(base + "/fetchDealer/" + dealers[0].id)
  ).json();
  assert.equal(detail[0].id, dealers[0].id);
  const original = await (
    await fetch(base + "/fetchReviews/dealer/" + dealers[0].id)
  ).json();
  assert.ok(Array.isArray(original));
  const review = {
    name: "Synthetic CI Driver",
    dealership: dealers[0].id,
    review: "Fantastic services",
    purchase: true,
    purchase_date: "2023-03-01",
    car_make: "Nissan",
    car_model: "Pathfinder",
    car_year: 2023,
  };
  const created = await fetch(base + "/insert_review", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Backend-Write-Token": process.env.BACKEND_WRITE_TOKEN,
    },
    body: JSON.stringify(review),
  });
  assert.equal(created.status, 201);
  const saved = await created.json();
  assert.ok(Number.isInteger(saved.id));
  const after = await (
    await fetch(base + "/fetchReviews/dealer/" + dealers[0].id)
  ).json();
  assert.ok(after.some((x) => x.id === saved.id && x.review === review.review));
  const invalid = await fetch(base + "/insert_review", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Backend-Write-Token": process.env.BACKEND_WRITE_TOKEN,
    },
    body: "{}",
  });
  assert.equal(invalid.status, 400);
  const unauthorized = await fetch(base + "/insert_review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(review),
  });
  assert.equal(unauthorized.status, 401);
  assert.equal((await fetch(base + "/fetchDealer/nope")).status, 400);
});
