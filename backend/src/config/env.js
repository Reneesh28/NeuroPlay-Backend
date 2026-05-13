const { z } = require("zod");

/**
 * 🌍 ENVIRONMENT CONFIGURATION SCHEMA
 * Validates core infrastructure and security requirements.
 */
const envSchema = z.object({
    // Server
    PORT: z.string().default("5000"),
    NODE_ENV: z.enum(["development", "production", "test"]).default("development"),

    // Databases
    MONGO_URI: z.string().url("MONGO_URI must be a valid connection string"),
    REDIS_HOST: z.string().default("127.0.0.1"),
    REDIS_PORT: z.string().default("6379"),
    REDIS_PASSWORD: z.string().optional(),

    // Security
    JWT_SECRET: z.string().min(16, "JWT_SECRET should be at least 16 characters for development").default("neuroplay-core-secret-2026"),
    
    // AI Engine
    AI_ENGINE_URL: z.string().url().default("http://127.0.0.1:8000"),

    // Cors
    ALLOWED_ORIGINS: z.string().default("http://localhost:3000,http://localhost:5173"),
});

function validateEnv() {
    try {
        const env = envSchema.parse(process.env);
        console.log("🌍 Environment variables validated successfully.");
        return env;
    } catch (err) {
        console.error("❌ Environment validation failed:");
        
        if (err instanceof z.ZodError) {
            err.errors.forEach(e => {
                console.error(`   - ${e.path.join(".")}: ${e.message}`);
            });
        } else {
            console.error(err.message || err);
        }
        
        console.error("\n💡 Please check your .env file or environment variables.");
        process.exit(1);
    }
}

module.exports = validateEnv;