(function () {

    var STORAGE_KEY = "pasabuy_latest_order";

    var current = null;

    function getInitials(name) {
        var words = name.trim().split(/\s+/);
        var first = words[0] ? words[0][0] : "";
        var second = words.length > 1 ? words[1][0] : "";
        return (first + second).toUpperCase();
    }

    function $(id) {
        return document.getElementById(id);
    }

    function formatTime(hours, minutes, spaced) {
        var period = hours >= 12 ? "PM" : "AM";
        hours = hours % 12 || 12;

        var mins = String(minutes).padStart(2, "0");
        var gap = spaced ? " " : "";

        return hours + ":" + mins + gap + period;
    }

    function showView(view) {
        $("formView").hidden = (view !== "form");
        $("orderView").hidden = (view !== "order");
        window.scrollTo(0, 0);
    }

    function saveOrder(order) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
        } catch (e) {
            // storage not available, ignore
        }
    }

    function addRow(qty, name) {
        var row = document.createElement("div");
        row.className = "r";

        row.innerHTML =
            '<input class="qty" type="number" min="1" value="' + (qty || 1) + '" aria-label="Quantity">' +
            '<input class="nm" type="text" placeholder="e.g. 2-pc Spicy ChickenJoy with Rice" aria-label="Item name">' +
            '<button type="button" class="rm" aria-label="Remove item">×</button>';

        row.querySelector(".nm").value = name || "";

        row.querySelector(".rm").onclick = function () {
            var rowCount = $("itemForm").querySelectorAll(".r").length;
            if (rowCount > 1) {
                row.remove();
            }
        };

        $("itemForm").insertBefore(row, $("addItem"));
    }

    function clearRows() {
        $("itemForm").querySelectorAll(".r").forEach(function (row) {
            row.remove();
        });
    }

    var addItemButton = document.createElement("button");
    addItemButton.type = "button";
    addItemButton.id = "addItem";
    addItemButton.className = "add-item";
    addItemButton.textContent = "+ Add item";
    addItemButton.onclick = function () {
        addRow();
    };

    $("itemForm").appendChild(addItemButton);
    addRow();

    $("fTip").addEventListener("input", function () {
        $("tipEcho").textContent = this.value || 0;
    });

    // Description character counter
    $("fDesc").addEventListener("input", function () {
        $("descCount").textContent = this.value.length;
    });

    $("submitOrder").onclick = function () {
        var target = $("fTarget").value.trim();
        var deliver = $("fDeliver").value.trim();
        var due = $("fDue").value;
        var name = $("fName").value.trim();
        var sid = $("fSid").value.trim();
        var items = [];

        $("itemForm").querySelectorAll(".r").forEach(function (row) {
            var itemName = row.querySelector(".nm").value.trim();
            var qty = parseInt(row.querySelector(".qty").value, 10) || 1;

            if (itemName) {
                items.push({
                    qty: Math.max(1, qty),
                    name: itemName
                });
            }
        });
        
        var missing = [];
        if (!name) missing.push("your name");
        if (!due) missing.push("a due time");
        if (!target) missing.push("a target store");
        if (!deliver) missing.push("where to deliver");
        if (items.length === 0) missing.push("at least one item");

        if (missing.length > 0) {
            $("err").textContent = "Add " + missing.join(", ") + ".";
            return;
        }
        $("err").textContent = "";

        // Build the order
        var now = new Date();
        var dueParts = due.split(":");

        var order = {
            id: Date.now(),
            posterName: name,
            posterSid: sid,
            target: target,
            deliver: deliver,
            items: items,
            desc: $("fDesc").value.trim(),
            tip: $("fTip").value || 0,
            due: formatTime(+dueParts[0], +dueParts[1], false),
            posted: formatTime(now.getHours(), now.getMinutes(), true)
        };

        saveOrder(order);
        renderOrder(order);
    };


    /* ==========================================================
       ORDER PAGE: show the posted order
       ========================================================== */

    function renderOrder(order) {
        current = order;

        // Title and time pill
        $("oTitle").textContent = "Deliver " + order.target + " order to " + order.deliver;
        $("oDue").textContent = order.due;
        $("oPosted").textContent = order.posted;

        // Order details
        $("oTarget").textContent = order.target;
        $("oBadge").textContent = order.items.length + (order.items.length === 1 ? " Item Listed" : " Items Listed");
        renderItems(order.items);

        // Description
        showDescription(order.desc);

        // Compensation
        var tip = Number(order.tip) || 0;
        $("oAmt").textContent = "₱ " + tip.toLocaleString("en-PH", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        $("oTipTxt").textContent = "(₱ " + tip + " Tip + Food Cost)";

        // Poster card (whoever filled in the form)
        var initials = getInitials(order.posterName);
        $("pAv").textContent = initials;
        $("cAv").textContent = initials;
        $("cAv2").textContent = initials;
        $("pName").textContent = order.posterName;
        $("pCount").textContent = 0;

        if (order.posterSid) {
            $("pSid").textContent = "Student ID " + order.posterSid;
            $("pSid").hidden = false;
            $("sidDot").hidden = false;
        } else {
            $("pSid").hidden = true;
            $("sidDot").hidden = true;
        }

        // Reset the claim button
        var claimButton = $("claimBtn");
        claimButton.disabled = false;
        claimButton.querySelector("span").textContent = "Accept & Claim Food Run";

        showView("order");
    }

    function renderItems(items) {
        var box = $("oItems");
        box.innerHTML = "";

        items.forEach(function (item) {
            var row = document.createElement("div");
            row.className = "row";

            var qty = document.createElement("span");
            qty.className = "q";
            qty.textContent = item.qty + "x";

            var name = document.createElement("span");
            name.textContent = item.name;

            row.appendChild(qty);
            row.appendChild(name);
            box.appendChild(row);
        });
    }


    /* ==========================================================
       ORDER PAGE: description (comment style, editable)
       ========================================================== */

    function showDescription(text) {
        $("oDesc").textContent = text || "No description yet.";
        $("descView").hidden = false;
        $("descEdit").hidden = true;
    }

    // Edit
    $("editDesc").onclick = function () {
        $("eDesc").value = (current && current.desc) ? current.desc : "";
        $("descView").hidden = true;
        $("descEdit").hidden = false;
        $("eDesc").focus();
    };

    // Cancel
    $("cancelDesc").onclick = function () {
        showDescription(current.desc);
    };

    // Save
    $("saveDesc").onclick = function () {
        current.desc = $("eDesc").value.trim();
        saveOrder(current);
        showDescription(current.desc);
    };


    /* ==========================================================
       BUTTONS: Post PasaBuy / Claim
       ========================================================== */

    // Header "Post PasaBuy" -> blank form
    $("goPost").onclick = function () {
        $("fName").value = "";
        $("fSid").value = "";
        $("fTarget").value = "";
        $("fDeliver").value = "";
        $("fDesc").value = "";
        $("fDue").value = "";
        $("fTip").value = 150;

        $("descCount").textContent = 0;
        $("tipEcho").textContent = 150;
        $("err").textContent = "";

        clearRows();
        addRow();
        showView("form");
    };

    // "Accept & Claim Food Run"
    $("claimBtn").onclick = function () {
        this.disabled = true;
        this.querySelector("span").textContent = "Food Run Claimed";
    };


    /* ==========================================================
       OTHER TABS: a newly posted order pops up here too
       ========================================================== */

    window.addEventListener("storage", function (e) {
        if (e.key === STORAGE_KEY && e.newValue) {
            try {
                renderOrder(JSON.parse(e.newValue));
            } catch (err) {
                // bad data, ignore
            }
        }
    });

})();