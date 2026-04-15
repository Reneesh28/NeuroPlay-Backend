const fs = require("fs-extra");
const path = require("path");

const TMP_DIR = path.join(__dirname, "../../uploads/tmp");
const FINAL_DIR = path.join(__dirname, "../../uploads/final");

async function saveChunk(uploadId, chunkIndex, buffer) {
    const dir = path.join(TMP_DIR, uploadId);
    await fs.ensureDir(dir);

    const filePath = path.join(dir, `${chunkIndex}.chunk`);
    await fs.writeFile(filePath, buffer);

    return filePath;
}

async function mergeChunks(uploadId, totalChunks, fileName) {
    const dir = path.join(TMP_DIR, uploadId);
    const finalPath = path.join(FINAL_DIR, `${uploadId}-${fileName}`);

    await fs.ensureDir(FINAL_DIR);

    const writeStream = fs.createWriteStream(finalPath);

    for (let i = 0; i < totalChunks; i++) {
        const chunkPath = path.join(dir, `${i}.chunk`);

        if (!fs.existsSync(chunkPath)) {
            throw new Error(`Missing chunk: ${i}`);
        }

        const data = await fs.readFile(chunkPath);
        writeStream.write(data);
    }

    writeStream.end();

    // cleanup
    await fs.remove(dir);

    return finalPath;
}

module.exports = {
    saveChunk,
    mergeChunks,
};