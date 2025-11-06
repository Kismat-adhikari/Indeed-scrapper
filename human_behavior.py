"""
Enhanced Human Behavior Simulation
==================================
Realistic human-like browsing patterns to avoid detection.
"""

import time
import random
import math
from typing import Dict, List, Tuple, Optional
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException


class HumanBehaviorSimulator:
    """Simulates realistic human browsing behavior."""
    
    def __init__(self, driver):
        self.driver = driver
        self.session_start_time = time.time()
        self.page_visit_count = 0
        self.last_activity_time = time.time()
        
        # Human behavior parameters (randomized per session)
        self.reading_speed = random.uniform(150, 400)  # words per minute
        self.scroll_preference = random.choice(['gradual', 'quick', 'mixed'])
        self.mouse_movement_style = random.choice(['precise', 'wandering', 'normal'])
        self.attention_span = random.uniform(30, 120)  # seconds before getting "distracted"
    
    def simulate_page_arrival(self):
        """Simulate human behavior when arriving at a new page."""
        self.page_visit_count += 1
        self.last_activity_time = time.time()
        
        # Initial page load wait (optimized - humans need time to process)
        initial_wait = random.uniform(0.8, 2.0)
        time.sleep(initial_wait)
        
        # Random chance of immediate back/forward (human mistake) - reduced frequency
        if random.random() < 0.02:  # 2% chance
            self._simulate_navigation_mistake()
        
        # Focus simulation (click somewhere safe)
        self._simulate_page_focus()
        
        # Initial scroll to get page dimensions
        self._simulate_initial_page_scan()
    
    def simulate_job_browsing(self, job_count: int) -> float:
        """
        Simulate human-like job browsing behavior.
        Returns the time spent on the page.
        """
        start_time = time.time()
        
        # Calculate realistic reading time based on job count
        estimated_reading_time = self._calculate_reading_time(job_count)
        
        # Simulate various browsing patterns
        patterns = [
            self._pattern_quick_scan,
            self._pattern_detailed_reading, 
            self._pattern_selective_browsing,
            self._pattern_comparison_browsing
        ]
        
        # Choose pattern based on session characteristics
        if self.page_visit_count <= 2:
            # First few pages - more detailed
            pattern = random.choices(
                patterns, 
                weights=[20, 50, 20, 10], 
                k=1
            )[0]
        else:
            # Later pages - more scanning
            pattern = random.choices(
                patterns,
                weights=[60, 15, 20, 5],
                k=1
            )[0]
        
        # Execute the selected browsing pattern
        pattern(job_count, estimated_reading_time)
        
        # Random chance of getting distracted/multitasking
        if random.random() < 0.15:  # 15% chance
            self._simulate_distraction()
        
        return time.time() - start_time
    
    def simulate_job_browsing_fast(self, job_count: int) -> float:
        """
        OPTIMIZED: Faster but still realistic job browsing behavior.
        Returns the time spent on the page.
        """
        start_time = time.time()
        
        # Calculate realistic reading time (50% faster than normal)
        estimated_reading_time = self._calculate_reading_time(job_count) * 0.5
        
        # Simplified browsing pattern - mostly quick scanning
        patterns = [
            self._pattern_quick_scan,
            self._pattern_selective_browsing,
        ]
        
        # Choose pattern
        pattern = random.choice(patterns)
        
        # Execute the selected browsing pattern with reduced time
        pattern(job_count, estimated_reading_time)
        
        # Reduced distraction chance
        if random.random() < 0.05:  # 5% chance instead of 15%
            time.sleep(random.uniform(0.5, 1.5))  # Shorter distraction
        
        return time.time() - start_time
    
    def _calculate_reading_time(self, job_count: int) -> float:
        """Calculate realistic reading time based on content."""
        # Estimate words per job posting (title + company + location + snippet)
        avg_words_per_job = random.randint(15, 35)
        total_words = job_count * avg_words_per_job
        
        # Reading time based on personal reading speed
        base_reading_time = (total_words / self.reading_speed) * 60  # seconds
        
        # Add scanning/processing time
        scanning_time = job_count * random.uniform(2, 8)  # seconds per job
        
        return base_reading_time + scanning_time
    
    def _pattern_quick_scan(self, job_count: int, estimated_time: float):
        """Quick scanning pattern - fast scrolling, minimal stops."""
        scroll_segments = random.randint(2, 4)  # Reduced segments
        time_per_segment = estimated_time * 0.3 / scroll_segments  # Use only 30% of estimated time
        
        for i in range(scroll_segments):
            # Quick scroll down
            self._scroll_smoothly(random.randint(400, 900), speed='fast')
            
            # Brief pause to "scan" (optimized)
            time.sleep(random.uniform(0.3, 1.0))
            
            # Occasional small scroll adjustments (reduced frequency)
            if random.random() < 0.2:
                self._scroll_smoothly(random.randint(-100, 100), speed='slow')
                time.sleep(random.uniform(0.2, 0.6))
    
    def _pattern_detailed_reading(self, job_count: int, estimated_time: float):
        """Detailed reading pattern - slower scrolling, longer pauses."""
        jobs_per_segment = random.randint(2, 4)
        segments = math.ceil(job_count / jobs_per_segment)
        
        for i in range(segments):
            # Scroll to next segment
            scroll_amount = random.randint(400, 700)
            self._scroll_smoothly(scroll_amount, speed='medium')
            
            # Longer reading pause
            reading_pause = random.uniform(3, 8)
            time.sleep(reading_pause)
            
            # Random mouse movements while "reading"
            if random.random() < 0.7:
                self._simulate_reading_mouse_movement()
            
            # Occasional re-reading (scroll up a bit, then down)
            if random.random() < 0.3:
                self._scroll_smoothly(random.randint(-200, -50), speed='slow')
                time.sleep(random.uniform(1, 3))
                self._scroll_smoothly(random.randint(100, 300), speed='medium')
    
    def _pattern_selective_browsing(self, job_count: int, estimated_time: float):
        """Selective browsing - stop at interesting jobs, skip others (optimized)."""
        current_position = 0
        jobs_processed = 0
        
        while jobs_processed < job_count:
            # Scroll to next job(s)
            scroll_amount = random.randint(300, 600)
            self._scroll_smoothly(scroll_amount, speed='fast')
            current_position += scroll_amount
            
            # Decide if this job is "interesting" (reduced interesting jobs)
            is_interesting = random.random() < 0.25  # 25% of jobs are interesting
            
            if is_interesting:
                # Shorter pause for interesting jobs
                time.sleep(random.uniform(1, 3))
                
                # Mouse movement to indicate reading (reduced frequency)
                if random.random() < 0.5:
                    self._simulate_job_card_interaction()
                
                # Less frequent scroll adjustments
                if random.random() < 0.3:
                    self._scroll_smoothly(random.randint(-50, 50), speed='slow')
                    time.sleep(random.uniform(0.5, 1.0))
            else:
                # Quick glance at uninteresting jobs
                time.sleep(random.uniform(0.2, 0.8))
            
            jobs_processed += random.randint(2, 4)  # Process 2-4 jobs per iteration
    
    def _pattern_comparison_browsing(self, job_count: int, estimated_time: float):
        """Comparison browsing - scrolling back and forth to compare jobs."""
        # Initial scan down
        self._scroll_smoothly(random.randint(800, 1200), speed='medium')
        time.sleep(random.uniform(2, 4))
        
        # Compare by scrolling up and down
        for i in range(random.randint(2, 4)):
            # Scroll up to compare
            self._scroll_smoothly(random.randint(-400, -200), speed='medium')
            time.sleep(random.uniform(2, 4))
            
            # Scroll back down
            self._scroll_smoothly(random.randint(300, 600), speed='medium')
            time.sleep(random.uniform(1, 3))
            
            # Random horizontal movement (side-by-side comparison feel)
            if random.random() < 0.6:
                self._simulate_horizontal_scanning()
    
    def _scroll_smoothly(self, amount: int, speed: str = 'medium'):
        """Smooth, human-like scrolling."""
        speed_map = {
            'slow': (0.05, 0.15),
            'medium': (0.02, 0.08), 
            'fast': (0.01, 0.03)
        }
        
        delay_range = speed_map.get(speed, speed_map['medium'])
        
        # Break scroll into smaller chunks for smooth movement
        chunks = random.randint(3, 8)
        chunk_size = amount // chunks
        
        for i in range(chunks):
            try:
                self.driver.execute_script(f"window.scrollBy(0, {chunk_size});")
                time.sleep(random.uniform(*delay_range))
            except WebDriverException:
                break
        
        # Small random final adjustment
        final_adjustment = random.randint(-20, 20)
        try:
            self.driver.execute_script(f"window.scrollBy(0, {final_adjustment});")
        except WebDriverException:
            pass
    
    def _simulate_page_focus(self):
        """Simulate clicking to focus on page (human behavior)."""
        try:
            # Click in a safe area (usually center-ish of page)
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            safe_x = random.randint(viewport_width // 4, 3 * viewport_width // 4)
            safe_y = random.randint(viewport_height // 4, 3 * viewport_height // 4)
            
            ActionChains(self.driver).move_by_offset(safe_x, safe_y).click().perform()
            time.sleep(random.uniform(0.1, 0.3))
        except WebDriverException:
            pass
    
    def _simulate_initial_page_scan(self):
        """Simulate initial page scanning behavior."""
        # Small initial scroll to see page content
        try:
            self.driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back to top (natural human behavior)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(0.3, 0.8))
        except WebDriverException:
            pass
    
    def _simulate_reading_mouse_movement(self):
        """Simulate mouse movement while reading."""
        try:
            actions = ActionChains(self.driver)
            
            # Generate natural reading-like mouse movements
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-50, 50)
                y_offset = random.randint(-20, 20)
                
                actions.move_by_offset(x_offset, y_offset)
                time.sleep(random.uniform(0.3, 0.8))
            
            actions.perform()
        except WebDriverException:
            pass
    
    def _simulate_job_card_interaction(self):
        """Simulate mouse interaction with job cards."""
        try:
            # Move mouse to simulate looking at job details
            actions = ActionChains(self.driver)
            
            # Simulate reading company name, title, etc.
            movements = [
                (random.randint(-30, 30), random.randint(-10, 10)),
                (random.randint(-20, 20), random.randint(20, 40)),
                (random.randint(-40, 40), random.randint(-5, 15))
            ]
            
            for x, y in movements:
                actions.move_by_offset(x, y)
                time.sleep(random.uniform(0.5, 1.2))
            
            actions.perform()
        except WebDriverException:
            pass
    
    def _simulate_horizontal_scanning(self):
        """Simulate horizontal eye/mouse movement (reading across)."""
        try:
            actions = ActionChains(self.driver)
            
            # Left to right scanning motion
            start_x = random.randint(-100, -50)
            end_x = random.randint(50, 100)
            steps = random.randint(3, 6)
            
            x_step = (end_x - start_x) // steps
            
            actions.move_by_offset(start_x, 0)
            
            for i in range(steps):
                actions.move_by_offset(x_step, random.randint(-5, 5))
                time.sleep(random.uniform(0.2, 0.5))
            
            actions.perform()
        except WebDriverException:
            pass
    
    def _simulate_navigation_mistake(self):
        """Simulate accidental navigation (human error)."""
        mistake_types = ['back_forward', 'accidental_click', 'key_press']
        mistake = random.choice(mistake_types)
        
        try:
            if mistake == 'back_forward':
                # Accidental back, then forward
                self.driver.execute_script("window.history.back();")
                time.sleep(random.uniform(0.5, 1.5))
                self.driver.execute_script("window.history.forward();")
                time.sleep(random.uniform(1.0, 2.0))
            
            elif mistake == 'accidental_click':
                # Quick click somewhere then move away
                actions = ActionChains(self.driver)
                actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
                actions.click()
                actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
                actions.perform()
                time.sleep(random.uniform(0.3, 0.8))
            
            elif mistake == 'key_press':
                # Accidental key press (like space or arrow)
                actions = ActionChains(self.driver)
                mistake_key = random.choice([Keys.SPACE, Keys.ARROW_DOWN, Keys.ARROW_UP])
                actions.send_keys(mistake_key)
                actions.perform()
                time.sleep(random.uniform(0.5, 1.0))
                
        except WebDriverException:
            pass
    
    def _simulate_distraction(self):
        """Simulate human distraction/multitasking."""
        distraction_types = ['pause', 'tab_switch', 'window_resize']
        distraction = random.choice(distraction_types)
        
        if distraction == 'pause':
            # Longer pause (checking phone, reading something else)
            pause_time = random.uniform(3, 10)
            time.sleep(pause_time)
        
        elif distraction == 'tab_switch':
            # Simulate tab switching (Ctrl+Tab)
            try:
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).send_keys(Keys.TAB).key_up(Keys.CONTROL)
                actions.perform()
                time.sleep(random.uniform(2, 5))
                # Switch back
                actions.key_down(Keys.CONTROL).send_keys(Keys.TAB).key_up(Keys.CONTROL)
                actions.perform()
            except WebDriverException:
                pass
        
        elif distraction == 'window_resize':
            # Minor window adjustments
            try:
                current_size = self.driver.get_window_size()
                new_width = current_size['width'] + random.randint(-50, 50)
                new_height = current_size['height'] + random.randint(-30, 30)
                
                self.driver.set_window_size(new_width, new_height)
                time.sleep(random.uniform(1, 2))
                
                # Restore original size
                self.driver.set_window_size(current_size['width'], current_size['height'])
            except WebDriverException:
                pass
    
    def simulate_session_break(self):
        """Simulate longer break between session pages (optimized)."""
        # Shorter random break duration
        break_duration = random.uniform(0.5, 2.0)
        
        print(f"   💤 Taking human-like break: {break_duration:.1f} seconds")
        time.sleep(break_duration)
        
        # Reduced chance of window interaction during break
        if random.random() < 0.1:
            try:
                # Minimize/restore or move window
                self.driver.minimize_window()
                time.sleep(random.uniform(1, 3))
                self.driver.maximize_window()
            except WebDriverException:
                pass
    
    def get_session_summary(self) -> Dict:
        """Get summary of human behavior patterns for this session."""
        session_duration = time.time() - self.session_start_time
        
        return {
            "session_duration_minutes": session_duration / 60,
            "pages_visited": self.page_visit_count,
            "reading_speed_wpm": self.reading_speed,
            "scroll_preference": self.scroll_preference,
            "mouse_style": self.mouse_movement_style,
            "avg_time_per_page": session_duration / max(self.page_visit_count, 1)
        }