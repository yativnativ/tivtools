#!/usr/bin/env python3
"""Splice the new light editorial theme CSS into build.py (replaces the old
dark-teal CSS assembly, lines 116-408 -> one new CSS = \"\"\"...\"\"\" block)."""
from pathlib import Path

P = Path("/Users/yannick/this-is-vegan/tools-site/build.py")

NEW = r'''CSS = """
:root{
--paper:#fbf6ee;--cream:#f6ece1;--ink:#0a3030;--ink2:#5f6f67;
--teal:#0a4a4a;--tealdeep:#0a3a30;--green:#29a579;--green-deep:#106050;--teal-card:#0a3a30;
--terra:#e59875;--terra-light:#f7b79a;--peach:#f8decd;
--card:#ffffff;--cardline:#efe3d2;--line:#e7dccb;--pill:#e3d6c4;
--yes:#2a9d6f;--no:#c0392b;--maybe:#d68a3a;
--serif:'Fraunces',Georgia,'Times New Roman',serif}
*{box-sizing:border-box;margin:0;padding:0}
@font-face{font-family:'Fraunces';font-style:normal;font-weight:400 900;font-display:swap;src:url(/fonts/fraunces-latin.woff2) format('woff2')}
@font-face{font-family:'Fraunces';font-style:italic;font-weight:400 700;font-display:swap;src:url(/fonts/fraunces-italic-latin.woff2) format('woff2')}
@font-face{font-family:'Bricolage Grotesque';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/bricolage-latin.woff2) format('woff2')}
html{scroll-behavior:smooth}
body{background:var(--paper);color:var(--ink);font-family:'Bricolage Grotesque',system-ui,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased;min-height:100vh}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
a{color:inherit}
img{max-width:100%}
/* header */
header.site{padding:20px 0 6px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none}
.brand .logo{height:34px;width:auto;display:block}
.brand .dot{display:none}
.brand small{display:none}
.free{font-family:'Bricolage Grotesque';font-weight:700;font-size:12px;letter-spacing:.02em;color:var(--green-deep);background:#fff;border:1.5px solid var(--peach);padding:8px 15px;border-radius:999px;white-space:nowrap}
.crumbs{padding:8px 0 0;font-size:13px;color:#8a9690}
.crumbs a{text-decoration:none}
.crumbs a:hover{text-decoration:underline}
.crumbs span{opacity:.6;margin:0 6px}
/* hero = dark colour-block panel */
.hero{position:relative;background:var(--teal);border-radius:32px;padding:42px 46px;margin-top:14px;overflow:hidden;text-align:center}
.hero::before{content:"";position:absolute;right:-90px;top:-130px;width:330px;height:330px;border-radius:50%;background:rgba(41,165,121,.15);pointer-events:none}
.hero.left{text-align:left}
.hero>*{position:relative}
.eyebrow{display:inline-block;font-family:'Bricolage Grotesque';font-weight:700;font-size:13px;letter-spacing:.02em;color:#8a4a2a;background:var(--peach);padding:8px 15px;border-radius:16px;margin-bottom:18px;box-shadow:0 6px 16px -8px rgba(0,0,0,.4);transform:rotate(-2deg)}
h1{font-family:var(--serif);font-weight:700;letter-spacing:-1px;font-size:clamp(38px,7vw,66px);line-height:1.02;color:var(--cream)}
h1.detail{font-size:clamp(32px,5.5vw,52px)}
h1 .q{color:var(--terra-light);font-style:italic}
.sub{margin:18px auto 0;max-width:480px;font-size:17px;color:var(--peach);opacity:.94}
.hero.left .sub{margin-left:0}
h2{font-family:var(--serif);font-weight:600;font-size:clamp(26px,4vw,34px);letter-spacing:-.3px;color:var(--ink)}
/* search */
.search-shell{margin:24px auto 0;max-width:480px;position:relative}
.hero.left .search-shell{margin-left:0}
.search-box{display:flex;align-items:center;gap:10px;background:var(--cream);border-radius:16px;padding:7px 7px 7px 18px;border:2px solid transparent;transition:border-color .15s}
.search-box:focus-within{border-color:var(--green)}
.search-box svg{flex:none;color:var(--green-deep)}
#q{flex:1;min-width:0;border:0;background:transparent;outline:none;font-family:'Bricolage Grotesque';font-weight:500;font-size:16px;color:var(--ink);padding:12px 0}
#q::placeholder{color:#9a8a78}
.go{flex:none;border:0;cursor:pointer;background:var(--green);color:#fff;font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;padding:13px 22px;border-radius:12px;transition:background .15s,transform .1s}
.go:hover{background:var(--green-deep)}
.go:active{transform:scale(.97)}
.chips{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin:14px auto 0;max-width:520px}
.hero.left .chips{justify-content:flex-start}
.chips span{font-size:12px;color:var(--peach);opacity:.65;align-self:center;margin-right:2px}
.chip{border:1px solid rgba(248,222,205,.32);background:transparent;color:var(--peach);font-family:'Bricolage Grotesque';font-weight:500;font-size:12.5px;padding:6px 13px;border-radius:999px;cursor:pointer;transition:all .14s}
.chip:hover{background:var(--peach);color:var(--ink);border-color:var(--peach)}
/* result card (light) */
#result{margin:26px auto 0;max-width:640px}
.hero .search-shell+.chips+#result,#result{}
.card{background:var(--card);color:var(--ink);border:1px solid var(--cardline);border-radius:20px;overflow:hidden;box-shadow:0 18px 44px -26px rgba(0,0,0,.45);animation:pop .28s cubic-bezier(.2,.9,.3,1.2);text-align:left}
@keyframes pop{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}
.verdict{display:flex;align-items:center;gap:14px;padding:18px 24px;color:#fff;font-family:var(--serif);font-weight:600}
.verdict.yes{background:var(--yes)}.verdict.no{background:var(--no)}.verdict.maybe{background:var(--maybe)}
.verdict .mark{width:38px;height:38px;flex:none;border-radius:50%;background:rgba(255,255,255,.22);display:grid;place-items:center;font-size:22px;font-family:'Bricolage Grotesque'}
.verdict .vtext{font-size:23px;letter-spacing:-.01em;line-height:1.1}
.verdict .vtext small{display:block;font-family:'Bricolage Grotesque';font-weight:600;font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.85}
.card-body{padding:22px 24px 24px}
.enum{font-family:var(--serif);font-weight:700;font-size:30px;letter-spacing:-.5px;color:var(--ink)}
.ename{font-family:'Bricolage Grotesque';font-weight:600;font-size:17px;color:var(--green-deep);margin-top:1px}
.klasse{display:inline-block;margin-top:12px;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--green-deep);background:rgba(16,96,80,.1);padding:5px 11px;border-radius:8px}
.info{margin-top:14px;font-size:16px;color:#3a4f4b}
.note{margin-top:14px;padding:13px 15px;border-radius:11px;font-size:14px;background:rgba(214,138,58,.12);border-left:3px solid var(--maybe);color:#7a4f1a;display:flex;gap:9px}
.note b{font-weight:700}
.detail-link{display:inline-block;margin-top:16px;font-family:'Bricolage Grotesque';font-weight:700;font-size:14px;color:var(--green-deep)}
.miss{background:var(--card);color:var(--ink);border:1px solid var(--cardline);border-radius:18px;padding:26px 24px;text-align:center;box-shadow:0 18px 44px -26px rgba(0,0,0,.4);animation:pop .28s ease}
.miss h3{font-family:var(--serif);font-weight:600;font-size:21px}
.miss p{margin-top:6px;color:#5f6f67;font-size:15px}
/* list + filters */
.listsec{margin-top:56px;padding-bottom:10px}
.listhead{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:18px}
.listhead p{font-size:14px;color:var(--ink2);max-width:360px;margin-top:2px}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.filt{cursor:pointer;border:1.5px solid var(--pill);background:#fff;color:var(--ink);font-family:'Bricolage Grotesque';font-weight:600;font-size:13px;padding:9px 15px;border-radius:999px;display:flex;align-items:center;gap:7px;transition:all .14s}
.filt .swatch{width:9px;height:9px;border-radius:50%}
.filt.s-yes .swatch{background:var(--yes)}.filt.s-no .swatch{background:var(--no)}.filt.s-maybe .swatch{background:var(--maybe)}
.filt.active{background:var(--ink);color:var(--cream);border-color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.item{background:#fff;border:1px solid var(--cardline);border-radius:15px;padding:15px 17px;cursor:pointer;transition:all .14s;display:flex;gap:12px;align-items:center;text-decoration:none;box-shadow:0 8px 22px -20px rgba(0,0,0,.4)}
.item:hover{transform:translateY(-2px);box-shadow:0 14px 30px -20px rgba(0,0,0,.45)}
.item .bar{width:5px;align-self:stretch;border-radius:4px;flex:none}
.item.yes .bar{background:var(--yes)}.item.no .bar{background:var(--no)}.item.maybe .bar{background:var(--maybe)}
.item .en{font-family:'Bricolage Grotesque';font-weight:700;font-size:16px;color:var(--ink)}
.item .nm{font-size:12.5px;color:#8a8073;margin-top:1px}
.item.hidden{display:none}
.empty{grid-column:1/-1;text-align:center;color:var(--ink2);padding:30px;font-size:15px;display:none}
/* generic sections */
.section{margin-top:52px}
.section h2{margin-bottom:14px}
.section p.lead{font-size:16px;color:var(--ink2);max-width:640px}
.prose{margin-top:16px;font-size:16px;color:#3a4f4b;max-width:640px}
.prose+.prose{margin-top:12px}
.prose a{color:var(--green-deep);font-weight:600;text-decoration:underline;text-decoration-color:rgba(16,96,80,.35)}
/* tool cards (hub) */
.toolcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:24px}
.toolcard{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:20px;padding:24px;box-shadow:0 14px 34px -26px rgba(0,0,0,.4);display:flex;flex-direction:column;gap:9px;text-decoration:none;transition:transform .14s,box-shadow .14s}
a.toolcard:hover{transform:translateY(-3px);box-shadow:0 22px 44px -26px rgba(0,0,0,.45)}
.toolcard.soon{background:rgba(248,222,205,.4);border:1px dashed var(--pill);box-shadow:none}
.toolcard .badge{align-self:flex-start;font-family:'Bricolage Grotesque';font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:5px 11px;border-radius:999px;background:var(--green);color:#fff}
.toolcard.soon .badge{background:var(--pill);color:#8a7a64}
.toolcard h3{font-family:var(--serif);font-weight:600;font-size:23px;letter-spacing:-.3px;color:var(--ink)}
.toolcard p{font-size:14.5px;color:var(--ink2)}
.toolcard .meta{margin-top:auto;padding-top:8px;font-family:'Bricolage Grotesque';font-size:13px;font-weight:700;color:var(--green-deep)}
.toolcard.soon .meta{color:#a8957f}
/* link list */
.linklist{margin-top:18px;display:grid;gap:10px;max-width:680px}
.linklist a{display:flex;align-items:center;justify-content:space-between;gap:14px;background:#fff;border:1px solid var(--cardline);border-radius:13px;padding:14px 18px;text-decoration:none;font-weight:600;font-size:15px;color:var(--ink);transition:all .14s}
.linklist a:hover{transform:translateY(-1px);box-shadow:0 12px 26px -20px rgba(0,0,0,.4)}
.linklist .arrow{color:var(--green);font-family:'Bricolage Grotesque';font-weight:700}
.related{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin-top:18px}
/* CTA = dark panel */
.cta{margin-top:46px;background:var(--tealdeep);border-radius:26px;padding:34px 38px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px;color:var(--cream)}
.cta h2{color:var(--cream)}
.cta p{font-size:14.5px;color:var(--peach);opacity:.9;margin-top:4px;max-width:520px}
.btn{display:inline-block;background:var(--green);color:#fff;font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;padding:14px 24px;border-radius:13px;text-decoration:none;transition:transform .1s,background .15s}
.btn:hover{transform:translateY(-1px);background:var(--green-deep)}
/* support block */
.support{position:relative;background:var(--peach);border-radius:28px;padding:38px 44px;margin-top:54px;overflow:hidden}
.support h2{color:#7a3f22}
.support p{color:#8a5638;font-size:15px;max-width:600px;margin-top:10px}
.slabel{font-family:'Bricolage Grotesque';font-weight:700;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:#a35c33;margin:22px 0 10px}
.sicons{display:flex;gap:10px;flex-wrap:wrap}
.sicon{width:46px;height:46px;border-radius:14px;background:#fff;display:flex;align-items:center;justify-content:center;color:var(--ink);text-decoration:none;border:1px solid #f0d6c2;transition:all .14s}
.sicon:hover{background:var(--green);color:#fff;border-color:var(--green);transform:translateY(-2px)}
.sicon svg{width:22px;height:22px}
.amts{display:flex;flex-wrap:wrap;gap:9px;align-items:center}
.amt{font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;background:#fff;border:1.5px solid #e6c3a8;color:#8a4a2a;padding:11px 18px;border-radius:12px;text-decoration:none;transition:transform .1s}
.amt:hover{transform:translateY(-1px)}
.amt.pri{background:var(--green);border-color:var(--green);color:#fff}
.amt.steady{background:transparent;border-color:#c98f63}
/* magazine article cards */
.arts{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}
.artcard{display:flex;gap:15px;background:#fff;border:1px solid var(--cardline);border-radius:18px;overflow:hidden;text-decoration:none;box-shadow:0 12px 28px -22px rgba(0,0,0,.4);transition:transform .14s}
.artcard:hover{transform:translateY(-2px)}
.artcard .thumb{flex:none;width:108px;background:var(--peach);background-size:cover;background-position:center}
.artcard .abody{padding:15px 16px 15px 0}
.artcard .kk{font-family:'Bricolage Grotesque';font-weight:700;font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--green)}
.artcard h3{font-family:var(--serif);font-weight:600;font-size:18px;line-height:1.18;margin:5px 0 4px;color:var(--ink)}
.artcard p{font-size:13px;color:#7a7064}
/* footer */
footer.site{margin-top:46px;border-top:1px solid var(--line);padding:32px 0 90px}
.frow{display:flex;flex-wrap:wrap;gap:22px;justify-content:space-between;align-items:center}
.flogo{height:30px;width:auto}
.flinks{display:flex;flex-wrap:wrap;gap:18px;font-family:'Bricolage Grotesque';font-weight:500;font-size:14px;color:var(--ink2)}
.flinks a{text-decoration:none}
.flinks a:hover{text-decoration:underline;color:var(--ink)}
.disc{font-size:12.5px;color:#9a9183;max-width:680px;line-height:1.6;margin-top:16px}
.disc b{color:#7a7264}
.sources{margin-top:10px;font-size:12px;color:#aaa093;max-width:680px}
.fbrand{display:none}
/* share bar (global) */
.pshare{position:fixed;left:16px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:9px;z-index:40;align-items:center}
.pshare .sl{writing-mode:vertical-rl;font-family:'Bricolage Grotesque';font-weight:700;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#a8957f;margin-bottom:2px}
.pshb{width:46px;height:46px;border-radius:50%;background:#fff;border:1px solid var(--cardline);display:flex;align-items:center;justify-content:center;color:var(--ink);text-decoration:none;box-shadow:0 8px 20px -10px rgba(0,0,0,.35);transition:transform .14s,background .14s,color .14s,border-color .14s}
.pshb:hover{transform:translateY(-2px)}
.pshb svg{width:21px;height:21px}
.pshb.wa:hover{background:#25D366;color:#fff;border-color:#25D366}
.pshb.ml:hover{background:var(--green);color:#fff;border-color:var(--green)}
.pshb.fb:hover{background:#1877F2;color:#fff;border-color:#1877F2}
.pshb.cp:hover{background:var(--ink);color:#fff;border-color:var(--ink)}
.pshb.cp.done{background:var(--green);color:#fff;border-color:var(--green)}
@media(max-width:1280px){
.pshare{left:0;right:0;top:auto;bottom:0;transform:none;flex-direction:row;justify-content:center;gap:11px;background:rgba(251,246,238,.95);border-top:1px solid var(--line);padding:9px 12px calc(9px + env(safe-area-inset-bottom))}
.pshare .sl{writing-mode:horizontal-tb;margin:0 2px 0 0;align-self:center}
.pshb{width:42px;height:42px;box-shadow:none}
}
/* hero emblem (illustration) */
.hero-illu{width:130px;height:130px;border-radius:28px;overflow:hidden;background:#fff;margin:0 auto 20px;box-shadow:0 20px 44px -20px rgba(0,0,0,.5);transform:rotate(-3deg);border:1px solid rgba(255,255,255,.6)}
.hero-illu img{width:100%;height:100%;object-fit:cover;display:block}
.hero.left .hero-illu{margin-left:0;margin-right:auto}
/* === Vegan-Ersatz-Finder === */
.subs{margin-top:18px;display:flex;flex-direction:column;gap:12px}
.colstack{display:flex;flex-direction:column;gap:12px}
.optcard{background:#fff;border-radius:14px;padding:15px 17px;border:1px solid var(--cardline)}
.optcard .sname{font-family:'Bricolage Grotesque';font-weight:700;font-size:17px;color:var(--ink);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.optcard .bf{font-family:'Bricolage Grotesque';font-weight:700;font-size:11px;letter-spacing:.03em;text-transform:uppercase;color:var(--green-deep);background:rgba(41,165,121,.13);padding:3px 9px;border-radius:999px}
.optcard .ratio{margin-top:5px;font-size:14px;color:var(--green-deep);font-weight:600}
.optcard .nt{margin-top:5px;font-size:14px;color:#3a4f4b}
.usecards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:18px}
.usecard{background:#fff;border:1px solid var(--cardline);border-radius:13px;padding:14px 16px}
.usecard b{font-family:'Bricolage Grotesque';font-weight:700;color:var(--ink);font-size:15px}
.usecard span{display:block;margin-top:3px;font-size:13px;color:var(--ink2)}
/* === Nährstoff-Rechner === */
.calc{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:20px;padding:24px;box-shadow:0 16px 40px -28px rgba(0,0,0,.4);max-width:640px;margin:26px auto 0}
.calc-grid{display:grid;grid-template-columns:1fr;gap:18px}
@media(min-width:620px){.calc-grid{grid-template-columns:1fr 1fr}}
.field{display:grid;gap:8px}
.field label{font-family:'Bricolage Grotesque';font-weight:700;font-size:14px;color:var(--ink)}
.field input[type=number],.field select{font-family:'Bricolage Grotesque';font-weight:700;font-size:18px;border:2px solid var(--pill);border-radius:12px;padding:12px 14px;background:#fff;color:var(--ink);width:100%}
.field input[type=number]:focus,.field select:focus{outline:none;border-color:var(--green)}
.seg{display:flex;gap:8px;flex-wrap:wrap}
.seg button{cursor:pointer;border:2px solid var(--pill);background:#fff;color:var(--ink);font-family:'Bricolage Grotesque';font-weight:600;font-size:14px;padding:10px 15px;border-radius:999px;transition:all .14s}
.seg button.on{background:var(--green-deep);border-color:var(--green-deep);color:#fff}
.nresults{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:12px;margin:24px auto 0;max-width:1080px}
.ncard{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:16px;padding:18px 20px;text-align:left;display:flex;flex-direction:column;box-shadow:0 12px 30px -26px rgba(0,0,0,.4)}
.ncard .nlabel{font-family:'Bricolage Grotesque';font-weight:700;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--green-deep)}
.ncard .nval{font-family:var(--serif);font-weight:700;font-size:30px;letter-spacing:-.5px;color:var(--ink);line-height:1.05;margin-top:3px}
.ncard .nunit{font-size:13px;color:#3a4f4b;font-weight:600;margin-top:1px}
.ncard .nsrc{margin-top:11px;font-size:13px;color:#5f6f67;flex:1}
.ncard .b2{align-self:flex-start;margin-top:11px;font-family:'Bricolage Grotesque';font-size:11px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;padding:3px 9px;border-radius:999px}
.b-ess{background:rgba(192,57,43,.13);color:#a02d20}
.b-opt{background:rgba(41,165,121,.13);color:var(--green-deep)}
.ncard .more{margin-top:11px;font-family:'Bricolage Grotesque';font-weight:700;font-size:13px;color:var(--green-deep);text-decoration:none}
.infobox{margin-top:24px;background:#fff;border:1px solid var(--cardline);border-left:3px solid var(--terra);border-radius:12px;padding:16px 18px;font-size:14px;color:#3a4f4b;max-width:1080px}
.infobox b{color:var(--ink)}
/* === Impact-Rechner === */
.iunit{display:flex;gap:10px;align-items:center;justify-content:center;flex-wrap:wrap;margin:22px auto 0;max-width:560px}
.hero.left .iunit{justify-content:flex-start}
.iunit input{font-family:var(--serif);font-weight:700;font-size:24px;width:120px;text-align:center;border:2px solid var(--cream);border-radius:13px;padding:12px;background:var(--cream);color:var(--ink)}
.iunit input:focus{outline:none;border-color:var(--green)}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:30px auto 0;max-width:760px}
@media(min-width:760px){.stats{grid-template-columns:repeat(4,1fr)}}
.stat{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:18px;padding:22px 16px;text-align:center;box-shadow:0 14px 34px -28px rgba(0,0,0,.4)}
.stat .snum{font-family:var(--serif);font-weight:700;font-size:clamp(26px,5vw,40px);letter-spacing:-.5px;line-height:1;color:var(--green-deep)}
.stat .slabel{font-family:'Bricolage Grotesque';font-weight:700;font-size:14px;margin-top:9px;color:var(--ink)}
.stat .seq{font-size:12px;color:#5f6f67;margin-top:6px;line-height:1.4}
/* === Saisonkalender === */
.months{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:22px auto 0;max-width:640px}
.months button{cursor:pointer;border:1.5px solid var(--pill);background:#fff;color:var(--ink);font-family:'Bricolage Grotesque';font-weight:600;font-size:13px;padding:8px 13px;border-radius:999px;transition:all .14s}
.months button:hover{border-color:var(--green)}
.months button.on{background:var(--ink);color:var(--cream);border-color:var(--ink)}
.subhead{font-family:var(--serif);font-weight:600;font-size:20px;margin:30px 0 12px;color:var(--ink);display:flex;align-items:center;gap:9px}
.subhead .swatch{width:10px;height:10px;border-radius:50%;background:var(--yes)}
.subhead.lager .swatch{background:var(--maybe)}
/* === Protein-Tabelle + Meal === */
.psort{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:16px auto 0}
.ptable{margin:10px auto 0;display:flex;flex-direction:column;max-width:720px;background:#fff;border:1px solid var(--cardline);border-radius:16px;padding:6px 18px;box-shadow:0 14px 34px -28px rgba(0,0,0,.4)}
.prow{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:13px 4px;border-bottom:1px solid var(--line)}
.prow:last-child{border-bottom:0}
.prow .pname{font-family:'Bricolage Grotesque';font-weight:700;font-size:16px;color:var(--ink)}
.prow .pcat{font-size:12px;color:#8a8073;margin-top:1px}
.prow .pval{font-family:var(--serif);font-weight:700;font-size:22px;letter-spacing:-.5px;color:var(--green-deep);white-space:nowrap}
.prow .pval small{font-size:11px;font-weight:600;color:#8a8073;font-family:'Bricolage Grotesque'}
.prow.top .pval{color:var(--green)}
.prow.tier .pval{color:#c0392b}
.prow.pflanz .pval{color:var(--green-deep)}
.addbtn{margin-top:4px;border:0;cursor:pointer;background:var(--green-deep);color:#fff;font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;padding:13px 22px;border-radius:13px;width:100%;transition:transform .1s}
.addbtn:active{transform:scale(.98)}
.rm{flex:none;width:30px;height:30px;border-radius:50%;border:0;background:rgba(192,57,43,.1);color:#a02d20;font-size:18px;cursor:pointer;line-height:1}
.mealsum{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:16px;padding:22px;text-align:center;margin:16px auto 0;max-width:720px}
.mealsum .big{font-family:var(--serif);font-weight:700;font-size:40px;color:var(--green-deep);letter-spacing:-.5px;line-height:1}
.mealsum .pct{font-size:14px;color:#5f6f67;margin-top:5px}
/* === Schriftarten-Generator === */
.fontinput{width:100%;max-width:640px;margin:26px auto 0;display:block;font-family:'Bricolage Grotesque';font-size:18px;border:2px solid var(--pill);border-radius:16px;padding:16px;background:#fff;color:var(--ink);resize:vertical;min-height:84px}
.fontinput:focus{outline:none;border-color:var(--green)}
.fontlist{margin:20px auto 0;display:flex;flex-direction:column;gap:10px;max-width:720px}
.fontrow{display:flex;align-items:center;justify-content:space-between;gap:14px;background:#fff;border:1px solid var(--cardline);color:var(--ink);border-radius:14px;padding:12px 16px}
.fontrow .flabel{display:block;font-family:'Bricolage Grotesque';font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--green-deep);margin-bottom:3px}
.fontrow .fout{font-size:18px;word-break:break-word;line-height:1.45;color:var(--ink)}
.copybtn{flex:none;border:0;cursor:pointer;background:var(--ink);color:var(--cream);font-family:'Bricolage Grotesque';font-weight:700;font-size:13px;padding:9px 14px;border-radius:10px;transition:background .15s}
.copybtn:hover{background:var(--green-deep)}
.copybtn.done{background:var(--green)}
.decogrid{display:flex;flex-wrap:wrap;gap:8px;max-width:720px;margin:14px auto 0;justify-content:center}
.decobtn{cursor:pointer;border:1.5px solid var(--pill);background:#fff;color:var(--ink);font-size:18px;padding:8px 13px;border-radius:11px;transition:all .14s}
.decobtn:hover{background:var(--ink);color:var(--cream);border-color:var(--ink)}
/* === Bild freistellen === */
.drop{max-width:560px;margin:26px auto 0;border:2px dashed var(--pill);border-radius:20px;padding:40px 24px;text-align:center;cursor:pointer;transition:all .15s;background:#fff}
.drop:hover,.drop.over{border-color:var(--green);background:rgba(41,165,121,.06)}
.drop .di{font-family:'Bricolage Grotesque';font-weight:700;font-size:19px;color:var(--ink)}
.drop .ds{font-size:14px;color:var(--ink2);margin-top:6px}
.bgstatus{max-width:560px;margin:14px auto 0;text-align:center;font-size:14px;color:var(--ink2);min-height:20px}
.bgbarwrap{max-width:560px;margin:12px auto 0;height:8px;background:var(--cream);border-radius:999px;overflow:hidden;display:none}
.bgbar{height:100%;width:5%;background:var(--green);transition:width .3s}
.bgresult{max-width:560px;margin:20px auto 0;display:none;text-align:center}
.checker{border-radius:16px;padding:14px;background-image:linear-gradient(45deg,#d8d8d8 25%,transparent 25%),linear-gradient(-45deg,#d8d8d8 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#d8d8d8 75%),linear-gradient(-45deg,transparent 75%,#d8d8d8 75%);background-size:22px 22px;background-position:0 0,0 11px,11px -11px,-11px 0;background-color:#fff}
.checker img{max-width:100%;border-radius:8px;display:block;margin:0 auto}
.bgswatches{display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap}
.sw{width:36px;height:36px;border-radius:10px;cursor:pointer;border:2px solid var(--pill);padding:0;transition:border-color .14s}
.sw.on{border-color:var(--ink)}
.sw.t{background-image:linear-gradient(45deg,#ccc 25%,transparent 25%),linear-gradient(-45deg,#ccc 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#ccc 75%),linear-gradient(-45deg,transparent 75%,#ccc 75%);background-size:12px 12px;background-position:0 0,0 6px,6px -6px,-6px 0;background-color:#fff}
.dlbtn{display:inline-block;margin-top:18px;background:var(--green);color:#fff;font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;padding:13px 24px;border-radius:13px;text-decoration:none;transition:transform .1s}
.dlbtn:active{transform:scale(.98)}
.hdtoggle{display:flex;align-items:center;gap:9px;justify-content:center;max-width:560px;margin:14px auto 0;font-size:14px;color:var(--ink2);cursor:pointer}
.hdtoggle input{width:17px;height:17px;accent-color:var(--green)}
/* === Veganizer === */
.kcard{background:#fff;color:var(--ink);border:1px solid var(--cardline);border-radius:20px;padding:24px;max-width:640px;margin:24px auto 0;text-align:left;box-shadow:0 18px 44px -28px rgba(0,0,0,.4);animation:pop .28s cubic-bezier(.2,.9,.3,1.2)}
.ktitle{font-family:var(--serif);font-weight:600;font-size:20px;color:var(--green-deep);margin-bottom:12px}
.kkonter{font-size:17px;line-height:1.5;color:var(--ink)}
.kfakt{margin-top:14px;font-size:14px;color:#3a4f4b;background:var(--cream);border-radius:11px;padding:12px 14px}
.kfakt .kq{display:block;margin-top:5px;font-size:12px;color:#7a7064}
.kstudie{display:inline-block;margin-top:8px;font-size:12px;font-weight:700;color:var(--green-deep);text-decoration:none;border-bottom:1px solid rgba(16,96,80,.35)}
.kstudie:hover{border-color:var(--green-deep)}
.klinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.klinks a{font-family:'Bricolage Grotesque';font-weight:600;font-size:13px;color:var(--green-deep);background:rgba(41,165,121,.12);padding:7px 12px;border-radius:999px;text-decoration:none}
.sharebar{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.sharebtn{cursor:pointer;border:0;font-family:'Bricolage Grotesque';font-weight:700;font-size:13px;padding:10px 16px;border-radius:11px;text-decoration:none;background:var(--ink);color:var(--cream);transition:background .15s}
.sharebtn:hover{background:var(--green-deep)}
.sharebtn.done{background:var(--green)}
.ctaline{margin-top:16px;font-size:14px;color:#3a4f4b}
.ctaline a{color:var(--green-deep);font-weight:700;text-decoration:none}
.qprog{font-size:13px;color:var(--ink2);margin-bottom:10px;text-align:center}
.qfrage{font-family:var(--serif);font-weight:600;font-size:22px;color:var(--ink);margin-bottom:16px;text-align:center;line-height:1.25}
.qopts{display:flex;flex-direction:column;gap:10px;max-width:640px;margin:0 auto}
.qopt{cursor:pointer;text-align:left;border:1px solid var(--cardline);background:#fff;color:var(--ink);font-family:'Bricolage Grotesque';font-weight:500;font-size:15px;padding:14px 16px;border-radius:13px;transition:all .14s;line-height:1.45}
.qopt:hover:not(:disabled){border-color:var(--green)}
.qopt.good{background:rgba(42,157,111,.14);border-color:var(--yes)}
.qopt.bad{background:rgba(192,57,43,.1);border-color:var(--no)}
.qopt.dim{opacity:.5}
.qfb{margin:14px auto 0;max-width:640px;font-size:15px;color:#3a4f4b;background:var(--cream);border-left:3px solid var(--terra);border-radius:11px;padding:12px 14px}
.qfb:empty{display:none}
#qnext{margin-top:16px;text-align:center}
.qdone{font-family:'Bricolage Grotesque';font-weight:700;color:var(--ink);font-size:17px}
.qdone .btn{margin-left:10px}
.vcardimg{display:block;max-width:340px;width:100%;height:auto;margin:18px auto 0;border-radius:18px;box-shadow:0 18px 44px -24px rgba(0,0,0,.5)}
/* === Hashtag-Helfer === */
.htags{display:flex;flex-wrap:wrap;gap:8px;max-width:760px;margin:22px auto 0;justify-content:center}
.htag{cursor:pointer;border:1.5px solid var(--pill);background:#fff;color:var(--ink);font-family:'Bricolage Grotesque';font-weight:600;font-size:14px;padding:8px 13px;border-radius:999px;transition:all .12s}
.htag:hover{border-color:var(--green)}
.htag.sel{background:var(--ink);color:var(--cream);border-color:var(--ink)}
.hcopybar{text-align:center;margin-top:22px}
.hcopy{cursor:pointer;border:0;background:var(--green-deep);color:#fff;font-family:'Bricolage Grotesque';font-weight:700;font-size:15px;padding:13px 26px;border-radius:13px;transition:background .15s}
.hcopy:hover{background:var(--green)}
.hcopy.done{background:var(--green)}
@media(max-width:620px){.hero{padding:30px 24px}.go{padding:13px 16px}.listhead{align-items:flex-start}.support{padding:30px 24px}.cta{padding:28px 24px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
""".strip()
'''

txt = P.read_text(encoding="utf-8")
lines = txt.split("\n")
assert lines[115].startswith("CSS = "), repr(lines[115])
assert lines[407].strip() == '"""', repr(lines[407])
new_lines = lines[:115] + NEW.split("\n") + lines[408:]
P.write_text("\n".join(new_lines), encoding="utf-8")
print("spliced ok, total lines now", len(new_lines))
