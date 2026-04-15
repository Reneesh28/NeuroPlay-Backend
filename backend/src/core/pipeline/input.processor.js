const path = require("path");

function detectInputType(input) {
    if (input.file_path) {
        const ext = path.extname(input.file_path).toLowerCase();

        if ([".mp4", ".avi", ".mov"].includes(ext)) {
            return "video";
        }

        if ([".jpg", ".jpeg", ".png"].includes(ext)) {
            return "image";
        }

        if (ext === ".txt") {
            return "mock_json"; // safer fallback for testing
        }
    }

    if (input.json_data) {
        return "json";
    }

    throw new Error(`Unsupported input type for input: ${JSON.stringify(input)}`);
}

function normalizeInput(rawInput) {
    const type = detectInputType(rawInput);

    let normalized = {
        type,
        data: {},
        meta: {
            source: "upload",
            created_at: Date.now(),
        },
    };

    switch (type) {
        case "video":
            normalized.data = {
                file_path: rawInput.file_path,
                format: path.extname(rawInput.file_path),
                file_name: path.basename(rawInput.file_path),
            };
            break;

        case "image":
            normalized.data = {
                file_path: rawInput.file_path,
                file_name: path.basename(rawInput.file_path),
            };
            break;

        case "mock_json":
            normalized.data = {
                payload: rawInput.json_data || rawInput.file_path, // fallback for txt test
            };
            break;

        default:
            throw new Error("Normalization failed");
    }

    return normalized;
}

module.exports = {
    normalizeInput,
};