// Reference = ECMAScript Number::toString, which is literally String(x) in JS.
// RFC 8785 sec 3.2.2.3 mandates exactly this for JSON numbers.
const vals = new Set();
const fixed = [0,-0,1,-1,0.1,1/3,1e-7,1e-6,1e21,1e20,1e-323,5e-324,
  Number.MAX_VALUE, Number.MIN_VALUE, 2**53, 2**53-1, -(2**53),
  9.109383e-31, 1.4e-45, 1e100, 1e-100, 123456789012345678901,
  333333333.33333329, 1e22, 9.999999999999999e20, 1.0000000000000002,
  4.5e-100, 1e-5, 1e-4, 0.000001, 0.0000001, 1e16, 1e17, 1e21-1,
  -1.7976931348623157e308, 5e-10, 6.02e23, 2.2250738585072014e-308];
for (const v of fixed) vals.add(v);
// random doubles across many magnitudes
let s = 88172645463325252n;
function xs(){ s^= s<<13n; s&=(1n<<64n)-1n; s^= s>>7n; s^= s<<17n; s&=(1n<<64n)-1n; return s; }
const buf = new ArrayBuffer(8); const dv = new DataView(buf);
for (let i=0;i<4000;i++){
  dv.setBigUint64(0, xs());
  const d = dv.getFloat64(0);
  if (Number.isFinite(d)) vals.add(d);
}
// simple decimals
for (let i=0;i<600;i++){ vals.add(i/7); vals.add(i*1e-9); vals.add(i*1e18); vals.add(Math.pow(10,i%40)); }
const out = [...vals].map(v => [v, String(v)]);
console.log(JSON.stringify(out));
