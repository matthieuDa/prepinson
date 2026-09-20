const supported = ["en", "fr", "nl", "de", "sv", "lb"];

function preferredLanguage(request) {
  const cookie = request.headers.get("cookie") || "";
  const saved = cookie.match(/(?:^|;\s*)prepinson-language=(en|fr|nl|de|sv|lb)(?:;|$)/);
  if (saved) return saved[1];

  const ranges = (request.headers.get("accept-language") || "")
    .split(",")
    .map((part) => {
      const [tag, quality = "q=1"] = part.trim().toLowerCase().split(";");
      return { code: tag.split("-")[0], q: Number(quality.replace("q=", "")) || 0 };
    })
    .filter(({ q }) => Number.isFinite(q) && q > 0 && q <= 1)
    .sort((a, b) => b.q - a.q);
  return ranges.find(({ code }) => supported.includes(code))?.code || "en";
}

export default async (request, context) => {
  const incoming = new URL(request.url);
  if (incoming.pathname !== "/") return context.next();
  const destination = new URL(`/${preferredLanguage(request)}/`, incoming.origin);
  destination.search = incoming.search;
  return new Response(null, {
    status: 302,
    headers: {
      location: destination.toString(),
      "cache-control": "private, no-store",
      vary: "Accept-Language, Cookie",
    },
  });
};
