const express = require("express");
const mongoose = require("mongoose");
const fs = require("fs");
const path = require("path");
const Reviews = require("./review");
const Dealerships = require("./dealership");
const app = express();
app.use(express.json({ limit: "32kb" }));
const wrap = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res)).catch(next);
app.get("/", (req, res) => res.json({ service: "Fullstack dealership API" }));
app.get(
  "/fetchReviews",
  wrap(async (req, res) => res.json(await Reviews.find().lean())),
);
app.get(
  "/fetchReviews/dealer/:id",
  wrap(async (req, res) => {
    if (!/^\d+$/.test(req.params.id))
      return res.status(400).json({ error: "Invalid dealer ID" });
    res.json(await Reviews.find({ dealership: Number(req.params.id) }).lean());
  }),
);
app.get(
  "/fetchDealers",
  wrap(async (req, res) =>
    res.json(await Dealerships.find().sort({ id: 1 }).lean()),
  ),
);
app.get(
  "/fetchDealers/:state",
  wrap(async (req, res) =>
    res.json(
      await Dealerships.find(
        req.params.state === "All" ? {} : { state: req.params.state },
      )
        .sort({ id: 1 })
        .lean(),
    ),
  ),
);
app.get(
  "/fetchDealer/:id",
  wrap(async (req, res) => {
    if (!/^\d+$/.test(req.params.id))
      return res.status(400).json({ error: "Invalid dealer ID" });
    res.json(await Dealerships.find({ id: Number(req.params.id) }).lean());
  }),
);
const Counter = mongoose.model(
  "fullstack_counter",
  new mongoose.Schema({ _id: String, value: Number }),
);
app.post(
  "/insert_review",
  wrap(async (req, res) => {
    if (
      !process.env.BACKEND_WRITE_TOKEN ||
      req.get("X-Backend-Write-Token") !== process.env.BACKEND_WRITE_TOKEN
    )
      return res
        .status(401)
        .json({ error: "Authorized backend access required" });
    const d = req.body;
    if (
      !d ||
      typeof d.review !== "string" ||
      !d.review.trim() ||
      d.review.length > 5000 ||
      typeof d.name !== "string" ||
      !d.name.trim() ||
      !Number.isInteger(d.dealership) ||
      !Number.isInteger(d.car_year) ||
      d.car_year < 2015 ||
      d.car_year > 2023 ||
      typeof d.purchase !== "boolean" ||
      typeof d.car_make !== "string" ||
      typeof d.car_model !== "string" ||
      !/^\d{4}-\d{2}-\d{2}$/.test(d.purchase_date)
    )
      return res.status(400).json({ error: "Invalid review" });
    if (!(await Dealerships.exists({ id: d.dealership })))
      return res.status(404).json({ error: "Dealer not found" });
    const counter = await Counter.findOneAndUpdate(
      { _id: "reviews" },
      { $inc: { value: 1 } },
      { new: true },
    );
    if (!counter) throw new Error("Counter not initialized");
    const saved = await Reviews.create({
      id: counter.value,
      name: d.name,
      dealership: d.dealership,
      review: d.review.trim(),
      purchase: d.purchase,
      purchase_date: d.purchase_date,
      car_make: d.car_make,
      car_model: d.car_model,
      car_year: d.car_year,
    });
    res.status(201).json(saved);
  }),
);
app.use((err, req, res, next) => {
  console.error("API failure:", err.name);
  res
    .status(err instanceof SyntaxError ? 400 : 500)
    .json({ error: "Request could not be completed" });
});
async function start() {
  if (!process.env.BACKEND_WRITE_TOKEN)
    throw new Error("BACKEND_WRITE_TOKEN is required");
  // Dedicated course database; never delete or reset an existing collection.
  await mongoose.connect(
    process.env.MONGO_URL ||
      "mongodb://127.0.0.1:27017/fullstack_capstone_20261018",
  );
  const dealers = JSON.parse(
    fs.readFileSync(path.join(__dirname, "data/dealerships.json"), "utf8"),
  ).dealerships;
  const reviews = JSON.parse(
    fs.readFileSync(path.join(__dirname, "data/reviews.json"), "utf8"),
  ).reviews;
  for (const d of dealers)
    await Dealerships.updateOne(
      { id: d.id },
      { $setOnInsert: d },
      { upsert: true },
    );
  for (const r of reviews)
    await Reviews.updateOne(
      { id: r.id },
      { $setOnInsert: r },
      { upsert: true },
    );
  const last = await Reviews.findOne().sort({ id: -1 }).lean();
  await Counter.updateOne(
    { _id: "reviews" },
    { $max: { value: last?.id || 0 } },
    { upsert: true },
  );
  console.log(
    `Fullstack seed ready: ${await Dealerships.countDocuments()} dealers, ${await Reviews.countDocuments()} reviews`,
  );
  return app.listen(Number(process.env.PORT || 3030), "0.0.0.0", () =>
    console.log("Fullstack API ready"),
  );
}
if (require.main === module)
  start().catch((err) => {
    console.error(err.name, "Startup failed");
    process.exitCode = 1;
  });
module.exports = { app, start };
