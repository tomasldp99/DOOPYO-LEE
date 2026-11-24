const origin = "https://innovation-maturity-insight.tomasldp.chatgpt.site";

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    const upstream = new URL(origin);
    upstream.pathname = incoming.pathname;
    upstream.search = incoming.search;

    const headers = new Headers(request.headers);
    headers.set("host", upstream.host);
    const response = await fetch(new Request(upstream, {
      method: request.method,
      headers,
      body: request.body,
      redirect: "manual",
    }));

    const responseHeaders = new Headers(response.headers);
    const location = responseHeaders.get("location");
    if (location) {
      const destination = new URL(location, upstream);
      if (destination.origin === origin) {
        responseHeaders.set("location", incoming.origin + destination.pathname + destination.search + destination.hash);
      }
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  },
};
