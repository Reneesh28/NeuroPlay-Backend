const mongoose = require('mongoose');
const id = 'e8a8b59e-eb87-4286-983e-7f2757a17ee8';
console.log('IsValid ObjectId:', mongoose.Types.ObjectId.isValid(id));
try {
    const query = { $or: [{ _id: id }, { job_id: id }] };
    console.log('Query:', JSON.stringify(query));
} catch (e) {
    console.error('Error constructing query:', e);
}
