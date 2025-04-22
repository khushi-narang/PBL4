/**
 * Three.js Helper Functions
 * This file contains utility functions for working with Three.js
 */

// Import Three.js modules from node_modules
const importThreeModules = async () => {
    try {
        // Create a script element for the main Three.js library
        const threeScript = document.createElement('script');
        threeScript.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
        document.head.appendChild(threeScript);
        
        // Wait for the main script to load
        await new Promise(resolve => {
            threeScript.onload = resolve;
        });
        
        // Now load additional modules
        const loaderScript = document.createElement('script');
        loaderScript.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js';
        document.head.appendChild(loaderScript);
        
        const orbitScript = document.createElement('script');
        orbitScript.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js';
        document.head.appendChild(orbitScript);
        
        // Wait for additional scripts to load
        await Promise.all([
            new Promise(resolve => { loaderScript.onload = resolve; }),
            new Promise(resolve => { orbitScript.onload = resolve; })
        ]);
        
        console.log('Three.js modules loaded successfully');
        return true;
    } catch (error) {
        console.error('Error loading Three.js modules:', error);
        return false;
    }
};

// Initialize the 3D environment
window.initThreeJS = async () => {
    const loaded = await importThreeModules();
    
    if (!loaded) {
        console.error('Failed to load Three.js modules');
        return false;
    }
    
    return true;
};