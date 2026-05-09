<template>
  <canvas ref="canvas" class="scene-backdrop" aria-hidden="true" />
  <div class="material-wash" :data-tone="tone" />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";
import gsap from "gsap";

const props = defineProps<{ tone: string }>();
const canvas = ref<HTMLCanvasElement | null>(null);

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let points: THREE.Points | null = null;
let lines: THREE.LineSegments | null = null;
let frame = 0;

const particleColor = 0x137f9a;
const lineColor = 0x8fc9d7;

function resize() {
  if (!renderer || !camera || !canvas.value) return;
  const { innerWidth, innerHeight } = window;
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}

function recolor() {
  if (!points || !lines) return;
  gsap.to((points.material as THREE.PointsMaterial).color, { r: new THREE.Color(particleColor).r, g: new THREE.Color(particleColor).g, b: new THREE.Color(particleColor).b, duration: 1.1 });
  gsap.to((lines.material as THREE.LineBasicMaterial).color, { r: new THREE.Color(lineColor).r, g: new THREE.Color(lineColor).g, b: new THREE.Color(lineColor).b, duration: 1.1 });
}

function animate() {
  if (!scene || !camera || !renderer || !points || !lines) return;
  points.rotation.y += 0.0007;
  points.rotation.x += 0.0002;
  lines.rotation.y -= 0.00042;
  camera.position.x = Math.sin(performance.now() * 0.00015) * 0.8;
  camera.lookAt(0, 0, 0);
  renderer.render(scene, camera);
  frame = requestAnimationFrame(animate);
}

onMounted(() => {
  if (!canvas.value) return;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0.8, 8.2);
  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const particleCount = 760;
  const positions = new Float32Array(particleCount * 3);
  for (let index = 0; index < particleCount; index += 1) {
    const radius = 2 + Math.random() * 4.8;
    const angle = Math.random() * Math.PI * 2;
    positions[index * 3] = Math.cos(angle) * radius;
    positions[index * 3 + 1] = (Math.random() - 0.5) * 5;
    positions[index * 3 + 2] = Math.sin(angle) * radius - 1.5;
  }
  const pointGeometry = new THREE.BufferGeometry();
  pointGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  points = new THREE.Points(pointGeometry, new THREE.PointsMaterial({ color: particleColor, size: 0.045, transparent: true, opacity: 0.78 }));
  scene.add(points);

  const lineCount = 260;
  const linePositions = new Float32Array(lineCount * 6);
  for (let index = 0; index < lineCount; index += 1) {
    const source = Math.floor(Math.random() * particleCount) * 3;
    const target = Math.floor(Math.random() * particleCount) * 3;
    linePositions.set(positions.slice(source, source + 3), index * 6);
    linePositions.set(positions.slice(target, target + 3), index * 6 + 3);
  }
  const lineGeometry = new THREE.BufferGeometry();
  lineGeometry.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
  lines = new THREE.LineSegments(lineGeometry, new THREE.LineBasicMaterial({ color: lineColor, transparent: true, opacity: 0.2 }));
  scene.add(lines);

  resize();
  window.addEventListener("resize", resize);
  animate();
});

watch(() => props.tone, recolor);

onBeforeUnmount(() => {
  cancelAnimationFrame(frame);
  window.removeEventListener("resize", resize);
  renderer?.dispose();
  points?.geometry.dispose();
  lines?.geometry.dispose();
});
</script>
