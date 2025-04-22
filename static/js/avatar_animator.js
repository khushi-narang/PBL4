/**
 * 3D Avatar Animator
 * Uses Three.js to animate a 3D avatar to perform sign language based on motion data
 */

class AvatarAnimator {
    constructor(container) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.avatar = null;
        this.mixer = null;
        this.clock = new THREE.Clock();
        this.animations = {};
        this.currentAction = null;
        this.isInitialized = false;
        this.queue = [];
        this.isPlaying = false;

        // Bind methods
        this.init = this.init.bind(this);
        this.animate = this.animate.bind(this);
        this.loadAvatar = this.loadAvatar.bind(this);
        this.playSign = this.playSign.bind(this);
        this.playSignSequence = this.playSignSequence.bind(this);
        this.onWindowResize = this.onWindowResize.bind(this);

        // Initialize if container is available
        if (this.container) {
            this.init();
        }

        // Handle window resize
        window.addEventListener('resize', this.onWindowResize);
    }

    /**
     * Initialize the 3D scene
     */
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x202124); // Dark background to match theme

        // Create camera
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(0, 1.5, 4);
        this.camera.lookAt(0, 1, 0);

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.container.appendChild(this.renderer.domElement);

        // Add lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 2, 3);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        this.scene.add(directionalLight);

        // Load avatar model
        this.loadAvatar();

        // Start animation loop
        this.animate();
        
        this.isInitialized = true;
        console.log('Avatar animator initialized');
    }

    /**
     * Animation loop
     */
    animate() {
        requestAnimationFrame(this.animate);

        if (this.mixer) {
            this.mixer.update(this.clock.getDelta());
        }

        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Load the 3D avatar model
     */
    loadAvatar() {
        // Use a placeholder/default model temporarily - we'll create a better one later
        const geometry = new THREE.BoxGeometry(0.5, 1.5, 0.5);
        const material = new THREE.MeshPhongMaterial({ color: 0x3f51b5 });
        this.avatar = new THREE.Mesh(geometry, material);
        this.avatar.position.set(0, 0.75, 0);
        this.scene.add(this.avatar);

        // We would load a GLTF model here in a full implementation
        // const loader = new THREE.GLTFLoader();
        // loader.load(
        //     '/static/models/avatar.glb',
        //     (gltf) => {
        //         this.avatar = gltf.scene;
        //         this.scene.add(this.avatar);
        //         this.mixer = new THREE.AnimationMixer(this.avatar);
        //         // Process animations
        //         if (gltf.animations && gltf.animations.length > 0) {
        //             gltf.animations.forEach(clip => {
        //                 this.mixer.clipAction(clip);
        //             });
        //         }
        //     },
        //     (xhr) => {
        //         console.log('Avatar loading progress: ' + (xhr.loaded / xhr.total * 100) + '%');
        //     },
        //     (error) => {
        //         console.error('Error loading avatar model:', error);
        //     }
        // );

        console.log('Avatar model loaded');
    }

    /**
     * Extract motion data from a video to animate the avatar
     * @param {string} videoPath Path to the sign language video
     * @param {string} glossWord The gloss word being signed
     */
    async extractMotionData(videoPath, glossWord) {
        // In a full implementation, we would analyze the video to extract motion data
        // For now, we'll use placeholder animations based on the gloss word
        
        console.log(`Extracting motion data for ${glossWord} from ${videoPath}`);
        
        // Create a simple animation based on the gloss word
        const animation = {
            duration: 1.5, // seconds
            keyframes: [
                { time: 0, position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 } },
                { time: 0.5, position: { x: 0.3, y: 0.2, z: 0 }, rotation: { x: 0, y: 0.5, z: 0 } },
                { time: 1.0, position: { x: -0.3, y: 0.1, z: 0 }, rotation: { x: 0, y: -0.5, z: 0 } },
                { time: 1.5, position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 } }
            ]
        };
        
        return animation;
    }

    /**
     * Play a sign animation for a specific gloss word
     * @param {string} videoPath Path to the sign language video
     * @param {string} glossWord The gloss word being signed
     * @returns {Promise} Promise that resolves when the animation completes
     */
    async playSign(videoPath, glossWord) {
        console.log(`Playing sign for ${glossWord}`);
        
        if (!this.isInitialized || !this.avatar) {
            console.warn('Avatar not initialized yet');
            return Promise.reject('Avatar not initialized');
        }
        
        // Extract motion data from the video
        const motionData = await this.extractMotionData(videoPath, glossWord);
        
        return new Promise((resolve) => {
            // Simple animation using the avatar's position and rotation
            const startTime = Date.now();
            const animate = () => {
                const elapsedTime = (Date.now() - startTime) / 1000; // convert to seconds
                
                if (elapsedTime < motionData.duration) {
                    // Find the keyframes to interpolate between
                    let startKeyframe = motionData.keyframes[0];
                    let endKeyframe = motionData.keyframes[1];
                    
                    for (let i = 1; i < motionData.keyframes.length; i++) {
                        if (elapsedTime <= motionData.keyframes[i].time) {
                            endKeyframe = motionData.keyframes[i];
                            startKeyframe = motionData.keyframes[i-1];
                            break;
                        }
                    }
                    
                    // Calculate interpolation factor
                    const factor = (elapsedTime - startKeyframe.time) / 
                                 (endKeyframe.time - startKeyframe.time);
                    
                    // Interpolate position
                    this.avatar.position.x = startKeyframe.position.x + 
                                          (endKeyframe.position.x - startKeyframe.position.x) * factor;
                    this.avatar.position.y = 0.75 + startKeyframe.position.y + 
                                          (endKeyframe.position.y - startKeyframe.position.y) * factor;
                    this.avatar.position.z = startKeyframe.position.z + 
                                          (endKeyframe.position.z - startKeyframe.position.z) * factor;
                    
                    // Interpolate rotation
                    this.avatar.rotation.x = startKeyframe.rotation.x + 
                                         (endKeyframe.rotation.x - startKeyframe.rotation.x) * factor;
                    this.avatar.rotation.y = startKeyframe.rotation.y + 
                                         (endKeyframe.rotation.y - startKeyframe.rotation.y) * factor;
                    this.avatar.rotation.z = startKeyframe.rotation.z + 
                                         (endKeyframe.rotation.z - startKeyframe.rotation.z) * factor;
                    
                    requestAnimationFrame(animate);
                } else {
                    // Reset avatar to default position
                    this.avatar.position.set(0, 0.75, 0);
                    this.avatar.rotation.set(0, 0, 0);
                    resolve();
                }
            };
            
            animate();
        });
    }

    /**
     * Play a sequence of sign animations
     * @param {Array} signs Array of objects with videoPath and glossWord properties
     */
    async playSignSequence(signs) {
        this.queue = [...signs];
        
        if (this.isPlaying) {
            console.log('Already playing a sequence, queued new sequence');
            return;
        }
        
        this.isPlaying = true;
        
        const playNext = async () => {
            if (this.queue.length === 0) {
                this.isPlaying = false;
                console.log('Finished playing sign sequence');
                return;
            }
            
            const sign = this.queue.shift();
            try {
                await this.playSign(sign.videoPath, sign.glossWord);
                // Add a small pause between signs
                setTimeout(playNext, 300);
            } catch (error) {
                console.error('Error playing sign:', error);
                playNext();
            }
        };
        
        playNext();
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        if (!this.camera || !this.renderer || !this.container) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
}

// Export the class
window.AvatarAnimator = AvatarAnimator;