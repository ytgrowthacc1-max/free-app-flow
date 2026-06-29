import { createFileRoute } from "@tanstack/react-router";
import { Onboarding } from "./index";

export const Route = createFileRoute("/experiences/$id")({
  head: () => ({
    meta: [
      { title: "App Builders — Free custom retention app for your Whop community" },
      {
        name: "description",
        content:
          "Tell us about your Whop community and we'll design (and build) a custom retention app for you — free.",
      },
      { property: "og:title", content: "App Builders — Free custom retention app" },
      {
        property: "og:description",
        content: "We design and build a custom retention app for your Whop community, free.",
      },
    ],
  }),
  component: Onboarding,
});
