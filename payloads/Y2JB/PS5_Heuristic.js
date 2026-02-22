(async () => {

    /* ================= Screen Clear ================= */
    await log("\n".repeat(120));
    await log("==================== PS5 Heuristic Testing ====================\n");

    const out = [];
    const push = (s = "") => out.push(s);

    /* ================= Core Feature Detection ================= */
    push("Core Feature Detection");
    push("-------------------------");

    const core = {};
    core.BigInt = typeof BigInt !== "undefined";
    core.SharedArrayBuffer = typeof SharedArrayBuffer !== "undefined";
    core.Atomics = typeof Atomics !== "undefined";
    core.WeakRef = typeof WeakRef !== "undefined";
    core.ArrayBuffer = typeof ArrayBuffer !== "undefined";
    core.WebAssembly = typeof WebAssembly !== "undefined";

    // Behavioral JIT probe (overrides UA)
    let jitWorks = false;
    try {
        const f = new Function("let x=0; for(let i=0;i<500;i++){x+=i}; return x;");
        jitWorks = f() === 124750;
    } catch (_) {}
    core.JIT = jitWorks;

    for (const [k, v] of Object.entries(core)) {
        push(`${k}: ${v ? "OK" : "FAIL"}`);
        await new Promise(r => setTimeout(r, 10)); // slight delay
    }

    push("");

    /* ================= Stress Tests ================= */
    push("Stress Tests");
    push("----------------------------------");

    const stress = {};
    const YIELD = () => new Promise(r => setTimeout(r, 1));

    // Array stress
    try {
        let arr = new Array(15000);
        for (let i = 0; i < arr.length; i++) {
            arr[i] = i;
            if ((i & 2047) === 0) await YIELD();
        }
        stress.Array = true;
        arr = null;
    } catch { stress.Array = false; }

    // BigInt stress
    try {
        let x = 1n;
        for (let i = 0; i < 30000; i++) {
            x = (x << 1n) ^ 1n;
            if ((i & 4095) === 0) await YIELD();
        }
        stress.BigInt = true;
    } catch { stress.BigInt = false; }

    // WeakRef usability
    try {
        let o = { a: 1 };
        let r = new WeakRef(o);
        o = null;
        for (let i = 0; i < 12000; i++) {
            r.deref();
            if ((i & 1023) === 0) await YIELD();
        }
        stress.WeakRef = true;
    } catch { stress.WeakRef = false; }

    // TypedArray sanity
    try {
        let b = new ArrayBuffer(2 * 1024 * 1024);
        let u = new Uint8Array(b);
        u[0] = 1;
        u[u.length - 1] = 2;
        stress.TypedArray = true;
    } catch { stress.TypedArray = false; }

    // WebAssembly sanity
    try {
        if (core.WebAssembly) {
            const wasmCode = new Uint8Array([
                0x00,0x61,0x73,0x6d,0x01,0x00,0x00,0x00,
                0x01,0x04,0x01,0x60,0x00,0x00,
                0x03,0x02,0x01,0x00,
                0x07,0x07,0x01,0x03,0x61,0x64,0x64,0x00,0x00,
                0x0a,0x09,0x01,0x07,0x00,0x41,0x01,0x41,0x02,0x6a,0x0b
            ]);
            const mod = new WebAssembly.Module(wasmCode);
            const inst = new WebAssembly.Instance(mod);
            stress.WebAssembly = typeof inst.exports.add === "function";
        } else stress.WebAssembly = false;
    } catch { stress.WebAssembly = false; }

    for (const [k, v] of Object.entries(stress)) {
        push(`${k} Stress: ${v ? "OK" : "FAIL"}`);
        await new Promise(r => setTimeout(r, 10));
    }

    push("");

    /* ================= Exploitability Assessment ================= */
    push("Exploitability Assessment");
    push("--------------------------");

    const userlandExec = core.JIT && core.SharedArrayBuffer && core.Atomics && core.WeakRef;
    push(`Userland Code Execution: ${userlandExec ? "Yes" : "No"}`);

    let kernelExploit = false;
    try {
        if (typeof FW_VERSION !== "undefined") {
            kernelExploit = Number(FW_VERSION) <= 10.01;
        }
    } catch (_) {}
    push(`Kernel Exploit: ${kernelExploit ? "Yes" : "No"}`);

    push(`WebKit Exploit Potential: ${userlandExec ? "Yes" : "No"}`);
    push("");

    /* ================= User-Agent / App Info ================= */
    push("System Info");
    push("---------------------");

    const ua = navigator.userAgent || "unknown";
    push(`Cobalt Version: ${ua.match(/Cobalt\/([\d.lts]+)/)?.[1] || "unknown"}`);
    push(`GLES: ${ua.includes("gles") ? "Yes" : "No"}`);
    push(`JIT Flag in UA: ${ua.includes("jitless") ? "jitless detected" : "not present"}`);

    const wk = ua.match(/AppleWebKit\/([\d.]+)/)?.[1] || "unknown";
    push(`WebKit Version: ${wk}`);
    const appMatch = ua.match(/YouTube_[^ ]+/);
    if (appMatch) push(`App Info: ${appMatch[0]}`);
    push(`FW_VERSION (Y2JB): ${typeof FW_VERSION !== "undefined" ? FW_VERSION : "not set"}`);
    push("");

    push("==================== Heuristic Complete ====================");

    /* ================= Print Everything ================= */
    for (const line of out) {
        await log(line);
        await new Promise(r => setTimeout(r, 25)); // slower output for readability
    }

})();
