# 📖 User Manual - Room Allocation System

Welcome to the Room Allocation System! This comprehensive guide will help you navigate and use all features of the application effectively.

## 🎯 Getting Started

### Accessing the Application

1. **Open your web browser**
2. **Navigate to the application URL**
   - Local: `http://localhost:8501`
   - Deployed: Your specific deployment URL
3. **Wait for the application to load**

The home page will display the current system status and quick action buttons.

## 🏠 Home Page Overview

The home page provides:

### System Information
- **Current Period**: Shows the active allocation period
- **Submissions Count**: Displays number of team and Oasis submissions
- **Last Reset**: Shows when the system was last reset

### Quick Actions
Four main action buttons for easy navigation:
- **📋 Submit Team Preference**: Go to project room submission
- **🌴 Submit Oasis Preference**: Go to Oasis workspace submission
- **📊 View Allocations**: See current room assignments
- **📈 View Analytics**: Access system analytics

### System Status
Real-time information about:
- Available rooms and capacities
- Current utilization rates
- System health indicators

## 📋 Project Room Allocation

### Understanding Project Rooms

Project rooms are allocated to teams for collaborative work sessions. Teams can choose between two day combinations:
- **Monday & Wednesday**
- **Tuesday & Thursday**

### Submitting Team Preferences

1. **Navigate to Project Rooms**
   - Click "📋 Submit Team Preference" on home page
   - Or use sidebar navigation

2. **Read the Instructions**
   - Teams must have 3-6 members
   - Choose preferred days
   - Each team can only submit once per period
   - Larger teams get priority in allocation

3. **Fill Out the Form**
   
   **Team Name** (Required)
   - Enter your team's name
   - Use only letters, numbers, spaces, hyphens, and underscores
   - Must be at least 2 characters long
   
   **Contact Person** (Required)
   - Enter the main contact person's name
   - Use only letters, spaces, hyphens, and apostrophes
   - Must be at least 2 characters long
   
   **Team Size** (Required)
   - Select from dropdown: 3, 4, 5, or 6 members
   - Larger teams get priority in allocation
   
   **Preferred Days** (Required)
   - Choose "Monday & Wednesday" OR "Tuesday & Thursday"
   - System will try to honor your preference

4. **Submit Your Preference**
   - Click "🚀 Submit Preference"
   - Wait for confirmation message
   - You'll see a success message with balloons animation

### Form Validation

The system validates all inputs:
- **Required fields**: All fields must be completed
- **Name validation**: Names must contain only valid characters
- **Team size**: Must be between 3-6 members
- **Duplicate prevention**: Each team can only submit once

### Rate Limiting

To prevent spam:
- Maximum 5 submissions per minute per team
- If exceeded, you'll see a countdown timer
- Wait for the timer to expire before trying again

## 🌴 Oasis Workspace Allocation

### Understanding Oasis Workspace

Oasis is a shared workspace for individual work. Features:
- **Capacity**: 11 people per day
- **Available Days**: Monday through Friday
- **Flexible Selection**: Choose 1-5 preferred days

### Submitting Oasis Preferences

1. **Navigate to Oasis Workspace**
   - Click "🌴 Submit Oasis Preference" on home page
   - Or use sidebar navigation

2. **Read the Instructions**
   - Individual workspace allocation
   - Select up to 5 preferred days
   - First-come, first-served with fairness algorithms

3. **Fill Out the Form**
   
   **Your Name** (Required)
   - Enter your full name
   - Use only letters, spaces, hyphens, and apostrophes
   - Must be at least 2 characters long
   
   **Preferred Days**
   - Check boxes for desired days: Monday through Friday
   - You can select 1-5 days
   - More selections increase your chances

4. **Submit Your Preference**
   - Click "🚀 Submit Preference"
   - Wait for confirmation message
   - Success message appears with balloons

### Oasis Capacity Information

The page displays real-time capacity:
- **Daily Limits**: 11 people per day
- **Current Usage**: How many spots are taken
- **Available Spots**: Remaining capacity
- **Color Coding**: Green (available), Yellow (limited), Red (full)

### Ad-hoc Addition

For urgent requests:
1. **Use the Ad-hoc Addition section**
2. **Contact administrators directly**
3. **Provide justification for urgent need**

## 📊 Viewing Current Allocations

### Allocation Overview

The allocations page shows:

#### Project Room Allocations
- **Team assignments** to specific rooms
- **Day and time** information
- **Room capacity** and utilization
- **Contact information** for each team

#### Oasis Workspace Allocations
- **Individual assignments** by day
- **Daily capacity** usage
- **Alphabetical listing** of assigned people

### Interactive Attendance Matrix

#### Purpose
- **Attendance tracking** for allocated individuals
- **Real-time updates** of who's present
- **Capacity monitoring** throughout the week

#### How to Use
1. **Find your name** in the matrix
2. **Click the checkbox** for days you're present
3. **Changes save automatically**
4. **View real-time attendance** of others

#### Matrix Features
- **Color coding**: Present (green), Absent (gray)
- **Daily totals**: Shows attendance count per day
- **Responsive design**: Works on mobile devices

### Allocation Status

Each allocation shows:
- **Assignment status**: Confirmed, Pending, or Waitlisted
- **Room/workspace details**: Location and capacity
- **Time slots**: When the allocation is active
- **Contact information**: How to reach team members

## 📈 Analytics Dashboard

### Overview Tab

#### Key Metrics
- **Total submissions**: Teams and individuals
- **Success rates**: Allocation efficiency
- **Capacity utilization**: How well resources are used

#### Success Rate Gauges
- **Visual indicators** of allocation success
- **Color coding**: Green (good), Yellow (moderate), Red (needs attention)
- **Percentage displays** for easy understanding

#### Capacity Charts
- **Room usage** bar charts
- **Daily utilization** patterns
- **Trend analysis** over time

### Project Rooms Analytics

#### Team Size Distribution
- **Pie chart** showing team size breakdown
- **Percentage breakdown** of 3, 4, 5, and 6-person teams

#### Day Preference Analysis
- **Bar chart** of preference popularity
- **Detailed breakdown** with percentages
- **Trend identification** for planning

#### Room Efficiency
- **Utilization rates** per room
- **Efficiency percentages** and color coding
- **Capacity vs. usage** comparison

### Oasis Analytics

#### Preference Patterns
- **Daily popularity** charts
- **Individual preference** distributions
- **Usage trend** analysis

#### Success Rates by Day
- **Daily allocation** success rates
- **Capacity utilization** by day
- **Demand vs. supply** analysis

### Trends Analysis

#### Submission Timeline
- **Daily submission** patterns
- **Peak usage** identification
- **Historical trends** over time

#### Demand vs. Capacity
- **Resource utilization** analysis
- **Capacity planning** insights
- **Optimization opportunities**

### Data Export

#### Available Exports
- **Team preferences**: CSV format
- **Oasis preferences**: CSV format
- **Project allocations**: CSV format
- **Oasis allocations**: CSV format
- **Summary reports**: Comprehensive overview

#### How to Export
1. **Navigate to Export tab**
2. **Choose data type** to export
3. **Click download button**
4. **File downloads** automatically
5. **Open in Excel** or other tools

## 🔧 Tips and Best Practices

### For Team Leaders

1. **Submit Early**
   - Submit preferences as soon as the period opens
   - Early submissions have better chances

2. **Be Flexible**
   - Consider both day options if possible
   - Larger teams have priority but limited flexibility

3. **Communicate**
   - Ensure all team members know the schedule
   - Share contact information for coordination

4. **Plan Ahead**
   - Check analytics for popular times
   - Consider off-peak preferences

### For Individual Users

1. **Multiple Preferences**
   - Select multiple days to increase chances
   - Be realistic about your availability

2. **Check Regularly**
   - Monitor allocation status
   - Use attendance matrix consistently

3. **Backup Plans**
   - Have alternative work arrangements
   - Consider different days if needed

### General Tips

1. **Browser Compatibility**
   - Use modern browsers (Chrome, Firefox, Safari, Edge)
   - Enable JavaScript for full functionality
   - Clear cache if experiencing issues

2. **Mobile Usage**
   - Application works on mobile devices
   - Portrait orientation recommended
   - Touch-friendly interface

3. **Data Connection**
   - Stable internet connection recommended
   - Changes save automatically
   - Refresh page if connection issues occur

## 🚨 Troubleshooting

### Common Issues

#### Form Won't Submit
**Possible Causes:**
- Missing required fields
- Invalid input format
- Rate limiting active
- Network connectivity issues

**Solutions:**
1. Check all required fields are filled
2. Verify input format (names, etc.)
3. Wait if rate limited
4. Refresh page and try again

#### Can't See Allocations
**Possible Causes:**
- No allocations made yet
- Page loading issues
- Browser cache problems

**Solutions:**
1. Wait for admin to run allocations
2. Refresh the page
3. Clear browser cache
4. Try different browser

#### Analytics Not Loading
**Possible Causes:**
- No data available yet
- Browser compatibility
- JavaScript disabled

**Solutions:**
1. Wait for data to accumulate
2. Enable JavaScript
3. Use supported browser
4. Refresh the page

#### Attendance Matrix Issues
**Possible Causes:**
- Not allocated to Oasis
- Browser compatibility
- Network issues

**Solutions:**
1. Verify you're allocated
2. Use supported browser
3. Check internet connection
4. Try mobile device

### Getting Help

If you continue experiencing issues:

1. **Check System Status**
   - Look for error messages
   - Check if others have same issue

2. **Try Basic Solutions**
   - Refresh the page
   - Clear browser cache
   - Try different browser
   - Check internet connection

3. **Contact Support**
   - Report specific error messages
   - Include browser and device information
   - Describe steps that led to the issue

## 📱 Mobile Usage

### Mobile Features

The application is fully responsive and works well on mobile devices:

#### Optimized Interface
- **Touch-friendly** buttons and forms
- **Responsive layout** adapts to screen size
- **Easy navigation** with mobile-optimized sidebar

#### Mobile-Specific Tips
1. **Portrait orientation** works best
2. **Zoom in** for detailed charts if needed
3. **Use native keyboard** for form inputs
4. **Swipe navigation** in some browsers

#### Mobile Limitations
- **Charts** may be smaller but remain interactive
- **Data entry** might be slower than desktop
- **File downloads** depend on browser settings

## 🔒 Privacy and Security

### Data Protection

Your data is protected through:
- **Input validation** prevents malicious data
- **Rate limiting** prevents abuse
- **Session management** ensures secure access
- **No personal data** stored beyond names and preferences

### What We Collect

The system only collects:
- **Team/individual names** for allocation purposes
- **Preferences** for room/workspace assignment
- **Usage statistics** for system improvement
- **No sensitive personal information**

### Data Retention

- **Active data** kept during allocation period
- **Archived data** preserved for analytics
- **No permanent storage** of personal details
- **Data reset** available for new periods

---

**Need more help? Contact your system administrator or check the FAQ section.**

