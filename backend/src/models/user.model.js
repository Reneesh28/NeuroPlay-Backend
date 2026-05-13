const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");

const UserSchema = new mongoose.Schema(
    {
        username: {
            type: String,
            required: true,
            unique: true,
            trim: true
        },
        email: {
            type: String,
            required: true,
            unique: true,
            trim: true,
            lowercase: true
        },
        password: {
            type: String,
            required: true,
            minlength: 8
        },
        role: {
            type: String,
            enum: ["user", "admin"],
            default: "user"
        },
        // Linked profile ID (optional, can also just match by user_id string)
        profile_id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "PlayerProfile"
        }
    },
    {
        timestamps: true
    }
);

// 🔥 Hash password before saving
UserSchema.pre("save", async function () {
    if (!this.isModified("password")) return;
    
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
});

// 🔥 Method to compare password
UserSchema.methods.comparePassword = async function (candidatePassword) {
    return bcrypt.compare(candidatePassword, this.password);
};

module.exports = mongoose.model("User", UserSchema);
