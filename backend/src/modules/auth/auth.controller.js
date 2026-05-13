const User = require('../../models/user.model');
const PlayerProfile = require('../../models/playerProfile.model');
const jwt = require('jsonwebtoken');
const { successResponse, errorResponse } = require('../../contracts/api.contract');
const { resolveDomain } = require('../../core/domain/domain.resolver');

const JWT_SECRET = process.env.JWT_SECRET || 'neuroplay-core-secret-2026';
const JWT_EXPIRES_IN = '7d';

/**
 * 🔐 REGISTER
 * Creates a new user and an associated empty PlayerProfile.
 * Uses atomic initialization to prevent orphaned accounts.
 */
async function register(req, res) {
    try {
        const { username, email, password, domain: requestedGameId } = req.body;

        if (!username || !email || !password) {
            return res.status(400).json(
                errorResponse({ message: "Missing required fields", code: "MISSING_FIELDS" }, { trace_id: req.traceId })
            );
        }

        // 1. Resolve Domain (e.g. bo6 -> blackops)
        const domain = resolveDomain(requestedGameId || "bo6");

        // 2. Check if user exists
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
            return res.status(400).json(
                errorResponse({ message: "Username or Email already registered", code: "USER_EXISTS" }, { trace_id: req.traceId })
            );
        }

        // 3. Create User
        const user = new User({ username, email, password });
        await user.save();

        try {
            // 4. 🔥 Initialize PlayerProfile (Digital Twin Identity)
            const profile = new PlayerProfile({
                user_id: user._id.toString(),
                domain: domain,
                preferred_style: "unknown"
            });
            await profile.save();

            // 5. Update user with profile ref
            user.profile_id = profile._id;
            await user.save();

            // 6. Generate Token
            const token = jwt.sign(
                { id: user._id, username: user.username, role: user.role, domain },
                JWT_SECRET,
                { expiresIn: JWT_EXPIRES_IN }
            );

            return res.status(201).json(
                successResponse({
                    token,
                    user: {
                        id: user._id,
                        username: user.username,
                        email: user.email,
                        role: user.role,
                        gameId: requestedGameId || "bo6"
                    },
                    profile_id: profile._id
                }, {
                    trace_id: req.traceId
                })
            );
        } catch (profileErr) {
            // Rollback User creation if Profile fails (Simulated Atomicity)
            await User.findByIdAndDelete(user._id);
            throw profileErr;
        }
    } catch (err) {
        return res.status(500).json(
            errorResponse(err, { trace_id: req.traceId })
        );
    }
}

/**
 * 🔐 LOGIN
 */
async function login(req, res) {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json(
                errorResponse({ message: "Email and Password required", code: "MISSING_CREDENTIALS" }, { trace_id: req.traceId })
            );
        }

        // 1. Find User
        const user = await User.findOne({ email }).populate('profile_id');
        if (!user) {
            return res.status(401).json(
                errorResponse({ message: "Invalid credentials", code: "INVALID_CREDENTIALS" }, { trace_id: req.traceId })
            );
        }

        // 2. Compare Password
        const isMatch = await user.comparePassword(password);
        if (!isMatch) {
            return res.status(401).json(
                errorResponse({ message: "Invalid credentials", code: "INVALID_CREDENTIALS" }, { trace_id: req.traceId })
            );
        }

        // 3. Generate Token
        const token = jwt.sign(
            { id: user._id, username: user.username, role: user.role, domain: user.profile_id?.domain || 'unknown' },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
        );

        return res.json(
            successResponse({
                token,
                user: {
                    id: user._id,
                    username: user.username,
                    email: user.email,
                    role: user.role,
                    gameId: user.profile_id?.domain === 'blackops' ? 'bo6' : 'mw3' // Best effort gameId recovery
                }
            }, {
                trace_id: req.traceId
            })
        );
    } catch (err) {
        return res.status(500).json(
            errorResponse(err, { trace_id: req.traceId })
        );
    }
}

/**
 * 🔐 GET CURRENT USER (ME)
 */
async function me(req, res) {
    try {
        const user = await User.findById(req.user.id).select('-password').populate('profile_id');
        if (!user) {
            return res.status(404).json(
                errorResponse({ message: "User not found", code: "USER_NOT_FOUND" }, { trace_id: req.traceId })
            );
        }

        return res.json(
            successResponse({
                user: {
                    id: user._id,
                    username: user.username,
                    email: user.email,
                    role: user.role,
                    profile: user.profile_id
                }
            }, {
                trace_id: req.traceId
            })
        );
    } catch (err) {
        return res.status(500).json(
            errorResponse(err, { trace_id: req.traceId })
        );
    }
}

module.exports = {
    register,
    login,
    me
};
