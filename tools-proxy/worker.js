// Serviert die statische Tool-Sammlung unter https://this-is-vegan.com/tools/
// Ursprung bleibt GitHub Pages (tools.this-is-vegan.com). Der Worker nimmt das
// /tools-Praefix aus dem Pfad und reicht den Rest an den Ursprung weiter.
const ORIGIN = "https://tools.this-is-vegan.com";

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname !== "/tools" && !url.pathname.startsWith("/tools/")) {
      return fetch(request);
    }

    // /tools -> /tools/ (eine kanonische Form, sonst doppelte URLs)
    if (url.pathname === "/tools") {
      return Response.redirect(`${url.origin}/tools/${url.search}`, 301);
    }

    const rest = url.pathname.slice("/tools".length) || "/";
    const target = new URL(rest + url.search, ORIGIN);

    const upstream = await fetch(target.toString(), {
      method: request.method,
      headers: request.headers,
      redirect: "manual",
    });

    // Ursprungs-Redirects auf den Praefix-Pfad zurueckbiegen
    const loc = upstream.headers.get("location");
    if (loc) {
      const abs = new URL(loc, ORIGIN);
      if (abs.host === new URL(ORIGIN).host) {
        const headers = new Headers(upstream.headers);
        headers.set("location", `/tools${abs.pathname}${abs.search}`);
        return new Response(null, { status: upstream.status, headers });
      }
    }

    const headers = new Headers(upstream.headers);
    headers.delete("x-frame-options");
    return new Response(upstream.body, { status: upstream.status, headers });
  },
};
