import Anthropic from "@anthropic-ai/sdk";

export async function POST(req) {
  try {
    const { messages, systemPrompt } = await req.json();

    const client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      system: systemPrompt,
      messages: messages,
    });

    return Response.json({ content: response.content[0].text });
  } catch (error) {
    console.error("Anthropic API error:", error);
    return Response.json(
      { error: "API call failed: " + error.message },
      { status: 500 }
    );
  }
}
