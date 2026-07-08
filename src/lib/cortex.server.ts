interface Message {
  role: "system" | "user" | "assistant";
  content: string;
}

export async function generateCortexResponse(
  systemPrompt: string,
  userMessageOrHistory: string | Message[]
): Promise<string> {
  const cortexKey = process.env.CORTEX_API_KEY;
  if (!cortexKey) {
    console.error("[ERROR] CORTEX_API_KEY is not set in environment");
    throw new Error("CORTEX_API_KEY is not set in environment");
  }

  const messages: Message[] = [{ role: "system", content: systemPrompt }];
  if (Array.isArray(userMessageOrHistory)) {
    for (const msg of userMessageOrHistory) {
      messages.push({
        role: msg.role as "user" | "assistant",
        content: msg.content,
      });
    }
  } else {
    messages.push({
      role: "user",
      content: userMessageOrHistory,
    });
  }

  const headers = {
    "Authorization": `Bearer ${cortexKey}`,
    "Content-Type": "application/json",
  };

  // Try Primary: Claude Sonnet 4.6 on claude.gg
  try {
    console.log("[INFO] Invoking Cortex AI (Primary: Claude Sonnet 4.6)...");
    const primaryRes = await fetch("https://claude.gg/v1/chat/completions", {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        messages,
        max_tokens: 2048,
      }),
    });

    if (primaryRes.ok) {
      const data = await primaryRes.json();
      const content = data?.choices?.[0]?.message?.content?.trim();
      if (content) {
        return content;
      }
    } else {
      const errText = await primaryRes.text().catch(() => "");
      console.warn(`[WARNING] Primary Claude API returned status ${primaryRes.status}: ${errText}`);
    }
  } catch (e) {
    console.warn(`[WARNING] Exception calling primary Claude API:`, e);
  }

  // Try Fallback: gpt-5 on api.claude.gg
  try {
    console.log("[INFO] Invoking Cortex AI (Fallback: gpt-5)...");
    const fallbackRes = await fetch("https://api.claude.gg/v1/chat/completions", {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: "gpt-5",
        messages,
        max_tokens: 2048,
      }),
    });

    if (fallbackRes.ok) {
      const data = await fallbackRes.json();
      const content = data?.choices?.[0]?.message?.content?.trim();
      if (content) {
        return content;
      }
    } else {
      const errText = await fallbackRes.text().catch(() => "");
      console.error(`[ERROR] Fallback gpt-5 API returned status ${fallbackRes.status}: ${errText}`);
    }
  } catch (e) {
    console.error(`[ERROR] Exception calling fallback gpt-5 API:`, e);
  }

  throw new Error("Cortex AI call failed both primary and fallback endpoints");
}
