import React, { useRef, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Float, Sparkles, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

export function HextechCrystal() {
    const meshRef = useRef<THREE.Mesh>(null);
    const coreRef = useRef<THREE.Mesh>(null);
    const { pointer } = useThree();

    // Create a randomized crystal-like geometry
    const geometry = useMemo(() => {
        return new THREE.OctahedronGeometry(2, 0); // Poly sharp edges
    }, []);

    useFrame((state, delta) => {
        if (meshRef.current) {
            const ambientY = state.clock.elapsedTime * 0.2;
            const ambientZ = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
            const targetX = pointer.y * 0.35;
            const targetY = ambientY + pointer.x * 0.45;
            const targetZ = ambientZ + pointer.x * 0.08;

            meshRef.current.rotation.x = THREE.MathUtils.lerp(meshRef.current.rotation.x, targetX, Math.min(1, delta * 4));
            meshRef.current.rotation.y = THREE.MathUtils.lerp(meshRef.current.rotation.y, targetY, Math.min(1, delta * 4));
            meshRef.current.rotation.z = THREE.MathUtils.lerp(meshRef.current.rotation.z, targetZ, Math.min(1, delta * 4));
        }

        if (coreRef.current) {
            const coreTargetX = pointer.y * 0.2;
            const coreTargetY = -pointer.x * 0.25;
            coreRef.current.rotation.x = THREE.MathUtils.lerp(coreRef.current.rotation.x, coreTargetX, Math.min(1, delta * 5));
            coreRef.current.rotation.y = THREE.MathUtils.lerp(coreRef.current.rotation.y, coreTargetY, Math.min(1, delta * 5));
        }
    });

    return (
        <group>
            {/* Floating animation wrapper */}
            <Float
                speed={2} // Animation speed
                rotationIntensity={0.5} // XYZ rotation intensity
                floatIntensity={1.5} // Up/down float intensity
            >
                <mesh ref={meshRef} geometry={geometry} scale={[1, 1.5, 1]}>
                    <MeshDistortMaterial
                        color="#00f0ff"
                        emissive="#00f0ff"
                        emissiveIntensity={0.5}
                        // Make it slightly transparent and glassy
                        transparent={true}
                        opacity={0.8}
                        metalness={0.9}
                        roughness={0.1}
                        distort={0.2} // Mild distortion for energy effect
                        speed={2}
                    />
                </mesh>

                {/* Inner Core */}
                <mesh ref={coreRef} scale={[0.5, 0.8, 0.5]}>
                    <octahedronGeometry args={[1.5, 0]} />
                    <meshStandardMaterial
                        color="#ffffff"
                        emissive="#ffffff"
                        emissiveIntensity={1.5}
                    />
                </mesh>
            </Float>

            {/* Magical Hextech Sparkles around the crystal */}
            <Sparkles
                count={50}
                scale={6}
                size={4}
                speed={0.4}
                opacity={0.5}
                color="#c8aa6f"
            />
            <Sparkles
                count={50}
                scale={8}
                size={2}
                speed={0.2}
                opacity={0.2}
                color="#00f0ff"
            />
        </group>
    );
}
