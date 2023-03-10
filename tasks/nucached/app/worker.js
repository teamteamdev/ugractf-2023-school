const startedDate = Date.now();


const flag = process.env["KYZYLBORDA_SECRET_flag"];


function escapeHTML(html) {
	return html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}


const STORES = {
	secrets: {
		writable: true,
		value: {
			flag
		}
	},
	main: {
		readable: true,
		writable: true,
		value: {
			hello: "Hello, world!"
		}
	}
};


function getKey(line) {
	const keys = line.split(".");
	const ns = keys.shift();

	let object = STORES;
	if(!object[ns]) {
		return `<i>non-existent namespace</i> ${escapeHTML(ns)}\n`;
	}

	if(!object[ns].readable) {
		return `<i>unreadable namespace</i> ${escapeHTML(ns)}\n`;
	}

	object = object[ns].value;
	for(const key of keys) {
		if(typeof object === "object" && object !== null) {
			if(!(key in object)) {
				return `<i>non-existent</i>\n`;
			} else {
				object = object[key];
			}
		} else {
			return `<i>operator . applied to a primitive</i>\n`;
		}
	}
	return escapeHTML(JSON.stringify(object) || "undefined") + "\n";
}


function setKey(line, value) {
	const keys = line.split(".");
	const ns = keys.shift();

	let object = STORES;
	if(!object[ns]) {
		object[ns] = {
			readable: true,
			writable: true,
			value: {}
		};
	}

	if(!object[ns].readable) {
		return `<i>unreadable namespace</i> ${escapeHTML(ns)}\n`;
	}
	if(!object[ns].writable) {
		return `<i>unwritable namespace</i> ${escapeHTML(ns)}\n`;
	}

	if(keys.length === 0) {
		object[ns].value = value;
		return `<i>success</i>\n`;
	} else {
		const lastKey = keys.pop();
		object = object[ns].value;
		for(const key of keys) {
			if(typeof object === "object" && object !== null) {
				if(!(key in object)) {
					return `<i>non-existent</i>\n`;
				} else {
					object = object[key];
				}
			} else {
				return `<i>operator . applied to a primitive</i>\n`;
			}
		}
		object[lastKey] = value;
		return `<i>success</i>\n`;
	}
}


function listKeys() {
	let result = "";
	for(const store in STORES) {
		result += `<i>Store</i> ${escapeHTML(store)}${STORES[store].readable ? "" : " <i>(unreadable)</i>"}${STORES[store].writable ? "" : " <i>(unwritable)</i>"}`;
		if(STORES[store].readable) {
			const value = STORES[store].value;
			if(typeof value === "object" && value !== null) {
				const state = {
					iters: 0
				};
				result += ":\n";
				result += listKeysImpl(value, "  ", state);
				if(state.iters > 100) {
					result += "<i>more lines not shown</i>\n";
				}
			} else {
				result += ` = ${escapeHTML(JSON.stringify(value) || "undefined")}\n`;
			}
		} else {
			result += " = ???\n";
		}
	}
	return result;
}

function listKeysImpl(object, prefix, state) {
	if(++state.iters > 100) {
		return "";
	}
	let result = "";
	for(const key in object) {
		result += `${escapeHTML(prefix + key)}`;
		if(typeof object[key] === "object" && object[key] !== null) {
			result += "\n" + listKeysImpl(object[key], `  ${prefix + key}.`, state)
		} else {
			result += ` = ${escapeHTML(JSON.stringify(object[key]) || "undefined")}\n`;
		}
	}
	return result;
}


module.exports = {
	escapeHTML,
	getKey,
	setKey,
	listKeys
};
