const bodyParser = require("body-parser");
const express = require("express");
const fs = require("fs");

const worker = require("./worker");


const app = express();
const router = express.Router();
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());

app.use(express.static("."));
app.use("/", router);

router.get("/:token/", (req, res, next) => {
	res.sendFile("userpage.html", {root: __dirname}, e => {
		if(e) {
			next(e);
		}
	});
});


function try_(fn) {
	try {
		return fn();
	} catch(e) {
		return `<span style="color: red">${worker.escapeHTML(e.toString())}</span>`;
	}
}

router.post("/:token/get-key", async (req, res) => {
	res.send(try_(() => worker.getKey(req.body.key.toString())));
});

router.post("/:token/set-key", async (req, res) => {
	res.send(try_(() => worker.setKey(req.body.key.toString(), req.body.value)));
});

router.post("/:token/list-keys", async (req, res) => {
	res.send(try_(() => worker.listKeys()));
});

app.listen("/tmp/app.sock");
