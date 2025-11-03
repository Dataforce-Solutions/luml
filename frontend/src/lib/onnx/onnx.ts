import * as ort from 'onnxruntime-web'

ort.env.wasm.wasmPaths = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@dev/dist/'
ort.env.wasm.numThreads = 1

console.info('[ONNX] WASM paths configured:', ort.env.wasm.wasmPaths)

export { ort }
