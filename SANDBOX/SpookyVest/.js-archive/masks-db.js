export const MASKS_DB = [
    {
        id: "meloni_screamer", name: "Meloni Screamer", type: "full_face",
        file: "meloni.png",
        anchors: { left_eye: [0.42, 0.42], right_eye: [0.58, 0.42] },
        blendMode: "source-over", opacity: 1, order: 10
    },
    {
        id: "moustache", name: "Moustache", type: "face_details",
        file: "moustache.png",
        placement: { facePoint: 13, maskPoint: [0.50, 0.50], reference: "eyes", widthFactor: 0.5, offset: [0, -0.02] },
        blendMode: "multiply", opacity: 0.9, order: 20
    },
    {
        id: "top_hat", name: "Top Hat", type: "accessory",
        file: "top_hat.png",
        placement: { facePoint: 10, maskPoint: [0.50, 0.90], reference: "eyes", widthFactor: 1.2, offset: [0, -0.15] },
        blendMode: "source-over", opacity: 1, order: 30
    }
];

export function getMaskById(id) { return MASKS_DB.find(m => m.id === id); }
export function resolveMaskUrl(mask, basePath) {
    return mask.url || (basePath.endsWith('/') ? basePath + mask.file : basePath + '/' + mask.file);
}
