class CircuitBreaker {
    constructor(maxFailures = 5, resetTimeout = 30000) {
        this.maxFailures = maxFailures;
        this.resetTimeout = resetTimeout;

        this.state = "CLOSED"; // CLOSED, OPEN, HALF_OPEN
        this.failureCount = 0;
        this.nextTry = 0;
    }

    async fire(requestFn, fallbackFn) {
        if (this.state === "OPEN") {
            if (Date.now() > this.nextTry) {
                console.log("[CIRCUIT BREAKER] HALF_OPEN - Testing external service.");
                this.state = "HALF_OPEN";
            } else {
                console.warn("[CIRCUIT BREAKER] OPEN - Fast failing request.");
                return fallbackFn();
            }
        }

        try {
            const result = await requestFn();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            // If the failure caused the breaker to open, fail fast using fallback
            if (this.state === "OPEN") {
                return fallbackFn();
            }
            throw error; // Otherwise, bubble up normal error
        }
    }

    onSuccess() {
        if (this.state !== "CLOSED") {
            console.log("[CIRCUIT BREAKER] CLOSED - Service recovered.");
        }
        this.failureCount = 0;
        this.state = "CLOSED";
    }

    onFailure() {
        this.failureCount++;
        if (this.failureCount >= this.maxFailures) {
            if (this.state !== "OPEN") {
                this.state = "OPEN";
                this.nextTry = Date.now() + this.resetTimeout;
                console.error(`[CIRCUIT BREAKER] TRIPPED! State is now OPEN. Suspending traffic for ${this.resetTimeout}ms.`);
            }
        }
    }
}

// Global instance for AI Engine
const aiCircuitBreaker = new CircuitBreaker(3, 30000); // 3 consecutive failures trips for 30s

module.exports = {
    CircuitBreaker,
    aiCircuitBreaker
};
