/**
 * Keeps at most MAX_IMAGES images in each request Pi sends, for every model.
 * The first image (the flowsheet itself) always stays; the rest of the allowance goes to the newest
 * images. Each dropped image is replaced by a line of text, so the model knows it has to open the
 * file again to see it.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const MAX_IMAGES = 2;
const NOTE = `[Image removed: only ${MAX_IMAGES} images fit in one request. The first image and the newest are kept. Read the file again to see this one.]`;

export default function (pi: ExtensionAPI) {
	pi.on("context", async (event) => {
		const images: { parts: any[]; index: number }[] = [];
		for (const message of event.messages as any[]) {
			if (!Array.isArray(message.content)) continue;
			message.content.forEach((part: any, index: number) => {
				if (part?.type === "image") images.push({ parts: message.content, index });
			});
		}
		if (images.length <= MAX_IMAGES) return;
		const dropped = images.slice(1, images.length - (MAX_IMAGES - 1));
		for (const { parts, index } of dropped) parts[index] = { type: "text", text: NOTE };
		return { messages: event.messages };
	});
}
