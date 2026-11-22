/**
 * Three guards for long agent runs, the same with or without the skill.
 * Loop guard: the third identical tool call in a row is blocked with a note telling the model to do
 * something else; the eighth ends the run. Written after a model ran the same zoom command 238 times in a
 * row and filled its context until the server failed.
 * Sweep guard: the thirtieth call in a row that differs from the one before only in its numbers ends the run.
 * Written after a model stepped one zoom box 10 pixels at a time, 388 times, past the edge of the drawing. Set from
 * the record: the longest such run in any attempt that wrote a chart was 19 calls, in a no-skill attempt 11.
 * Finish guard: if the model stops before flowsheet.mmd exists, it is told the task is not finished and
 * the run carries on, at most twice. Written after a model ended a turn mid-thought, with no tool call and
 * no chart, which ended the whole run.
 */
import { existsSync } from "node:fs";
import { join } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const WARN_AT = 3;
const STOP_AT = 8;
const NUDGES = 2;
const SWEEP_STOP = 30;

export default function (pi: ExtensionAPI) {
	let last = "";
	let count = 0;
	let lastShape = "";
	let sweep = 0;
	pi.on("tool_call", async (event: any, ctx: any) => {
		const signature = `${event.toolName} ${JSON.stringify(event.input)}`;
		count = signature === last ? count + 1 : 1;
		last = signature;
		const shape = signature.replace(/\d+/g, "#");
		sweep = shape === lastShape ? sweep + 1 : 1;
		lastShape = shape;
		if (sweep >= SWEEP_STOP) {
			ctx.abort();
			return { block: true, reason: `Stopped: ${sweep} calls in a row that differ only in their numbers.` };
		}
		if (count >= STOP_AT) {
			ctx.abort();
			return { block: true, reason: `Stopped: the same call ${count} times in a row.` };
		}
		if (count >= WARN_AT) {
			return {
				block: true,
				reason: `Not run: you have made this exact call ${count} times in a row and it will not give anything new. ` +
					"Do something different now.",
			};
		}
	});

	let nudged = 0;
	pi.on("agent_before_settle", async (event: any, ctx: any) => {
		if (nudged >= NUDGES || existsSync(join(ctx.cwd, "flowsheet.mmd"))) return;
		nudged += 1;
		return {
			entries: [...event.entries, {
				type: "custom_message",
				customType: "finish-guard",
				content: "The task is not finished: flowsheet.mmd has not been written yet. Carry on from where you are.",
				display: false,
			}],
			continue: true,
		};
	});
}
