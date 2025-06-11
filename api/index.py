from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Enhanced HTML template with modern UI/UX and advanced filtering
HTML_TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tableau Bulk Extract Refresh</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.29.0/feather.min.js"></script>
  <style>
    body { background-color: #f8fafc; }
    .main-container { background-color: #ffffff; }
    .card { 
      background: white; 
      border-radius: 12px; 
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
      border: 1px solid #e5e7eb;
    }
    .card:hover { 
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
      transition: box-shadow 0.2s ease-in-out;
    }
    .hover-lift { transition: transform 0.2s ease-in-out; }
    .hover-lift:hover { transform: translateY(-1px); }
    .animate-fade-in { animation: fadeIn 0.5s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .filter-badge { transition: all 0.2s ease; }
    .filter-badge:hover { transform: scale(1.05); }
    .workbook-card { 
      transition: all 0.3s ease; 
      border-left: 4px solid transparent;
      background: #fafafa;
      border: 1px solid #e5e7eb;
    }
    .workbook-card:hover { 
      border-left-color: #3b82f6; 
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      background: white;
    }
    .stats-card { 
      background: white; 
      border: 1px solid #e5e7eb;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .header-bg { background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); }
    .input-field {
      border: 1px solid #d1d5db;
      background: white;
    }
    .input-field:focus {
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    .tooltip {
      position: relative;
      display: inline-block;
    }
    .tooltip .tooltip-text {
      visibility: hidden;
      width: 320px;
      background-color: #1f2937;
      color: #fff;
      text-align: left;
      border-radius: 8px;
      padding: 12px;
      position: absolute;
      z-index: 1000;
      bottom: 125%;
      left: 50%;
      margin-left: -160px;
      opacity: 0;
      transition: opacity 0.3s;
      font-size: 14px;
      line-height: 1.4;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .tooltip .tooltip-text::after {
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: #1f2937 transparent transparent transparent;
    }
    .tooltip:hover .tooltip-text {
      visibility: visible;
      opacity: 1;
    }
    .tooltip-icon {
      color: #6b7280;
      cursor: help;
      transition: color 0.2s;
    }
    .tooltip-icon:hover {
      color: #3b82f6;
    }
  </style>
</head>
<body class="min-h-screen bg-gray-50">
  <div class="min-h-screen p-4 md:p-8">
    <!-- Header -->
    <div class="text-center mb-8 animate-fade-in">
      <div class="header-bg rounded-2xl p-8 card mb-8">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-2">
          <i data-feather="server" class="inline-block w-8 h-8 mr-2"></i>
          Tableau Extract Manager
        </h1>
        <p class="text-blue-100 text-lg">Modern bulk extract refresh with advanced filtering</p>
      </div>
    </div>

    <!-- Main Container -->
    <div class="max-w-7xl mx-auto space-y-8">
      
      <!-- Authentication Section -->
      <div class="card p-8 hover-lift animate-fade-in">
        <div class="flex items-center mb-6">
          <i data-feather="key" class="w-6 h-6 text-blue-600 mr-3"></i>
          <h2 class="text-2xl font-bold text-gray-900">Authentication</h2>
        </div>
        
        <form id="authForm" class="grid md:grid-cols-2 gap-4">
          <div class="space-y-4">
            <div class="relative">
              <i data-feather="globe" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
              <input type="text" id="serverUrl" class="input-field w-full pl-12 pr-4 py-3 rounded-xl focus:outline-none" placeholder="Server URL" value="https://10az.online.tableau.com" required>
            </div>
            <div class="relative">
              <i data-feather="folder" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
              <input type="text" id="site" class="input-field w-full pl-12 pr-4 py-3 rounded-xl focus:outline-none" placeholder="Site Content URL" value="thenavigators01" required>
            </div>
          </div>
          <div class="space-y-4">
            <div class="relative">
              <i data-feather="user" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
              <input type="text" id="tokenName" class="input-field w-full pl-12 pr-12 py-3 rounded-xl focus:outline-none" placeholder="PAT Name" required>
              <div class="tooltip absolute right-3 top-3">
                <i data-feather="help-circle" class="w-5 h-5 tooltip-icon"></i>
                <span class="tooltip-text">
                  <strong>How to create a Personal Access Token:</strong><br/>
                  1. Sign in to Tableau Server<br/>
                  2. Go to your user menu → My Account Settings<br/>
                  3. Navigate to Personal Access Tokens<br/>
                  4. Click "Create new token"<br/>
                  5. Enter a token name and click "Create"<br/>
                  6. Copy both the token name and secret
                </span>
              </div>
            </div>
            <div class="relative">
              <i data-feather="lock" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
              <input type="password" id="tokenSecret" class="input-field w-full pl-12 pr-12 py-3 rounded-xl focus:outline-none" placeholder="PAT Secret" required>
              <div class="tooltip absolute right-3 top-3">
                <i data-feather="help-circle" class="w-5 h-5 tooltip-icon"></i>
                <span class="tooltip-text">
                  <strong>Personal Access Token Secret:</strong><br/>
                  This is the secret value generated when you create a PAT.<br/><br/>
                  <strong>Important:</strong> The secret is only shown once when created, so make sure to copy it immediately. If you lose it, you'll need to create a new token.
                </span>
              </div>
            </div>
          </div>
          <div class="md:col-span-2">
            <button type="submit" id="signInBtn" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300 hover-lift">
              <i data-feather="log-in" class="inline-block w-5 h-5 mr-2"></i>
              <span>Connect & Load Workbooks</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Stats Dashboard -->
      <div id="statsSection" class="hidden animate-fade-in">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="stats-card rounded-2xl p-6 text-center">
            <div class="text-3xl font-bold text-gray-800" id="totalWorkbooks">0</div>
            <div class="text-gray-600 text-sm">Total Workbooks</div>
          </div>
          <div class="stats-card rounded-2xl p-6 text-center">
            <div class="text-3xl font-bold text-green-600" id="selectedCount">0</div>
            <div class="text-gray-600 text-sm">Selected</div>
          </div>
          <div class="stats-card rounded-2xl p-6 text-center">
            <div class="text-3xl font-bold text-blue-600" id="projectCount">0</div>
            <div class="text-gray-600 text-sm">Projects</div>
          </div>
          <div class="stats-card rounded-2xl p-6 text-center">
            <div class="text-3xl font-bold text-purple-600" id="ownerCount">0</div>
            <div class="text-gray-600 text-sm">Owners</div>
          </div>
        </div>
      </div>

      <!-- Workbook Management Section -->
      <div id="workbookSection" class="hidden animate-fade-in">
        <div class="card p-8">
          
          <!-- Search and Filter Controls -->
          <div class="mb-8">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center">
                <i data-feather="filter" class="w-6 h-6 text-blue-600 mr-3"></i>
                <h2 class="text-2xl font-bold text-gray-900">Workbook Management</h2>
              </div>
              <div class="flex space-x-3">
                <button id="selectAllButton" class="px-6 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors hover-lift">
                  <i data-feather="check-square" class="inline-block w-4 h-4 mr-2"></i>
                  Select All
                </button>
                <button id="clearAllButton" class="px-6 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors hover-lift">
                  <i data-feather="square" class="inline-block w-4 h-4 mr-2"></i>
                  Clear All
                </button>
              </div>
            </div>

            <!-- Search Bar -->
            <div class="relative mb-6">
              <i data-feather="search" class="absolute left-4 top-4 w-5 h-5 text-gray-400"></i>
              <input type="text" id="searchInput" class="input-field w-full pl-12 pr-4 py-4 rounded-xl focus:outline-none text-lg" placeholder="Search workbooks by name, owner, or project...">
            </div>

            <!-- Filter Controls -->
            <div class="grid md:grid-cols-3 gap-4 mb-6">
              <div>
                <label class="block text-gray-700 mb-2 font-medium">Filter by Project</label>
                <select id="projectFilter" class="input-field w-full p-3 rounded-xl focus:outline-none">
                  <option value="">All Projects</option>
                </select>
              </div>
              <div>
                <label class="block text-gray-700 mb-2 font-medium">Filter by Owner</label>
                <select id="ownerFilter" class="input-field w-full p-3 rounded-xl focus:outline-none">
                  <option value="">All Owners</option>
                </select>
              </div>
              <div>
                <label class="block text-gray-700 mb-2 font-medium">Sort By</label>
                <select id="sortBy" class="input-field w-full p-3 rounded-xl focus:outline-none">
                  <option value="name">Name (A-Z)</option>
                  <option value="name_desc">Name (Z-A)</option>
                  <option value="project">Project</option>
                  <option value="owner">Owner</option>
                  <option value="updated">Last Updated</option>
                  <option value="created">Created Date</option>
                </select>
              </div>
            </div>

            <!-- Active Filters Display -->
            <div id="activeFilters" class="flex flex-wrap gap-2 mb-4"></div>
          </div>

          <!-- Workbook List -->
          <div id="workbookList" class="max-h-96 overflow-y-auto space-y-4 mb-8"></div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4">
            <button id="refreshButton" class="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-700 transition-all duration-300 hover-lift">
              <i data-feather="refresh-cw" class="inline-block w-5 h-5 mr-2"></i>
              <span>Refresh Selected Extracts</span>
            </button>
            <button id="exportButton" class="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 hover-lift">
              <i data-feather="download" class="inline-block w-5 h-5 mr-2"></i>
              Export List
            </button>
          </div>
        </div>
      </div>

      <!-- Activity Log -->
      <div class="card p-8 animate-fade-in">
        <div class="flex items-center mb-4">
          <i data-feather="activity" class="w-6 h-6 text-blue-600 mr-3"></i>
          <h2 class="text-2xl font-bold text-gray-900">Activity Log</h2>
          <button id="clearLogButton" class="ml-auto px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
            <i data-feather="trash-2" class="inline-block w-4 h-4 mr-1"></i>
            Clear
          </button>
        </div>
        <div id="log" class="bg-gray-50 text-gray-700 p-6 rounded-xl h-48 overflow-y-auto font-mono text-sm border"></div>
      </div>
    </div>
  </div>

  <script>
    // Initialize Feather icons
    feather.replace();
    
    let server = '', siteId = '', authToken = '';
    let allWorkbooks = [];
    let filteredWorkbooks = [];

    // Utility functions
    function logMessage(message, type = 'info') {
      const log = document.getElementById('log');
      const timestamp = new Date().toLocaleTimeString();
      const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
      log.innerHTML += `[${timestamp}] ${icon} ${message}\n`;
      log.scrollTop = log.scrollHeight;
    }

    function updateStats() {
      const totalWorkbooks = allWorkbooks.length;
      const selectedCount = document.querySelectorAll('.workbookCheckbox:checked').length;
      const projectCount = new Set(allWorkbooks.map(wb => wb.project)).size;
      const ownerCount = new Set(allWorkbooks.map(wb => wb.owner)).size;

      document.getElementById('totalWorkbooks').textContent = totalWorkbooks;
      document.getElementById('selectedCount').textContent = selectedCount;
      document.getElementById('projectCount').textContent = projectCount;
      document.getElementById('ownerCount').textContent = ownerCount;
    }

    function populateFilters() {
      const projectFilter = document.getElementById('projectFilter');
      const ownerFilter = document.getElementById('ownerFilter');
      
      // Clear existing options (except "All")
      projectFilter.innerHTML = '<option value="">All Projects</option>';
      ownerFilter.innerHTML = '<option value="">All Owners</option>';
      
      // Get unique values
      const projects = [...new Set(allWorkbooks.map(wb => wb.project))].sort();
      const owners = [...new Set(allWorkbooks.map(wb => wb.owner))].sort();
      
      projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project;
        option.textContent = project;
        projectFilter.appendChild(option);
      });
      
      owners.forEach(owner => {
        const option = document.createElement('option');
        option.value = owner;
        option.textContent = owner;
        ownerFilter.appendChild(option);
      });
    }

    function applyFilters() {
      const searchTerm = document.getElementById('searchInput').value.toLowerCase();
      const projectFilter = document.getElementById('projectFilter').value;
      const ownerFilter = document.getElementById('ownerFilter').value;
      const sortBy = document.getElementById('sortBy').value;

      filteredWorkbooks = allWorkbooks.filter(wb => {
        const matchesSearch = !searchTerm || 
          wb.name.toLowerCase().includes(searchTerm) ||
          wb.project.toLowerCase().includes(searchTerm) ||
          wb.owner.toLowerCase().includes(searchTerm);
        
        const matchesProject = !projectFilter || wb.project === projectFilter;
        const matchesOwner = !ownerFilter || wb.owner === ownerFilter;
        
        return matchesSearch && matchesProject && matchesOwner;
      });

      // Sort workbooks
      filteredWorkbooks.sort((a, b) => {
        switch(sortBy) {
          case 'name_desc': return b.name.localeCompare(a.name);
          case 'project': return a.project.localeCompare(b.project) || a.name.localeCompare(b.name);
          case 'owner': return a.owner.localeCompare(b.owner) || a.name.localeCompare(b.name);
          case 'updated': return new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0);
          case 'created': return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
          default: return a.name.localeCompare(b.name);
        }
      });

      displayWorkbooks();
      updateActiveFilters();
    }

    function updateActiveFilters() {
      const container = document.getElementById('activeFilters');
      container.innerHTML = '';
      
      const searchTerm = document.getElementById('searchInput').value;
      const projectFilter = document.getElementById('projectFilter').value;
      const ownerFilter = document.getElementById('ownerFilter').value;
      
      if (searchTerm) addFilterBadge(container, 'Search', searchTerm, () => document.getElementById('searchInput').value = '');
      if (projectFilter) addFilterBadge(container, 'Project', projectFilter, () => document.getElementById('projectFilter').value = '');
      if (ownerFilter) addFilterBadge(container, 'Owner', ownerFilter, () => document.getElementById('ownerFilter').value = '');
    }

    function addFilterBadge(container, label, value, clearFunc) {
      const badge = document.createElement('div');
      badge.className = 'filter-badge bg-blue-500 text-white px-3 py-1 rounded-full text-sm flex items-center cursor-pointer';
      badge.innerHTML = `${label}: ${value} <i data-feather="x" class="w-4 h-4 ml-2"></i>`;
      badge.onclick = () => { clearFunc(); applyFilters(); };
      container.appendChild(badge);
      feather.replace();
    }

    function displayWorkbooks() {
      const container = document.getElementById('workbookList');
      container.innerHTML = '';
      
      if (filteredWorkbooks.length === 0) {
        container.innerHTML = `
          <div class="text-center py-12 text-gray-500">
            <i data-feather="inbox" class="w-16 h-16 mx-auto mb-4 opacity-50"></i>
            <p class="text-xl mb-2">No workbooks found</p>
            <p class="text-gray-400">Try adjusting your filters or search terms</p>
          </div>
        `;
        feather.replace();
        return;
      }

      // Group by project
      const projectGroups = {};
      filteredWorkbooks.forEach(wb => {
        if (!projectGroups[wb.project]) {
          projectGroups[wb.project] = [];
        }
        projectGroups[wb.project].push(wb);
      });

      Object.keys(projectGroups).sort().forEach(projectName => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'bg-white/90 rounded-2xl p-6 mb-4';
        
        const projectHeader = document.createElement('div');
        projectHeader.className = 'flex items-center justify-between mb-4';
        
        const projectTitle = document.createElement('h3');
        projectTitle.className = 'font-bold text-xl text-gray-800 flex items-center';
        projectTitle.innerHTML = `<i data-feather="folder" class="w-5 h-5 mr-2"></i> ${projectName} <span class="ml-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">${projectGroups[projectName].length}</span>`;
        
        const projectActions = document.createElement('div');
        projectActions.className = 'flex space-x-2';
        
        const selectProjectBtn = document.createElement('button');
        selectProjectBtn.className = 'px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors';
        selectProjectBtn.innerHTML = '<i data-feather="check-square" class="w-4 h-4 mr-1"></i> Select All';
        selectProjectBtn.onclick = () => {
          projectDiv.querySelectorAll('.workbookCheckbox').forEach(cb => cb.checked = true);
          updateStats();
        };
        
        projectActions.appendChild(selectProjectBtn);
        projectHeader.appendChild(projectTitle);
        projectHeader.appendChild(projectActions);
        projectDiv.appendChild(projectHeader);
        
        const workbookGrid = document.createElement('div');
        workbookGrid.className = 'grid md:grid-cols-2 gap-4';
        
        projectGroups[projectName].forEach(wb => {
          const wbCard = document.createElement('div');
          wbCard.className = 'workbook-card bg-gray-50 rounded-xl p-4 border-l-4';
          
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.value = wb.id;
          checkbox.className = 'workbookCheckbox float-right mt-1';
          checkbox.onchange = updateStats;
          
          const content = document.createElement('div');
          content.className = 'pr-8';
          
          const name = document.createElement('div');
          name.className = 'font-semibold text-gray-900 mb-2';
          name.textContent = wb.name;
          
          const meta = document.createElement('div');
          meta.className = 'text-sm text-gray-600 space-y-1';
          meta.innerHTML = `
            <div><i data-feather="user" class="w-4 h-4 inline mr-1"></i> ${wb.owner}</div>
            ${wb.createdAt ? `<div><i data-feather="calendar" class="w-4 h-4 inline mr-1"></i> Created: ${new Date(wb.createdAt).toLocaleDateString()}</div>` : ''}
            ${wb.updatedAt ? `<div><i data-feather="clock" class="w-4 h-4 inline mr-1"></i> Updated: ${new Date(wb.updatedAt).toLocaleDateString()}</div>` : ''}
          `;
          
          content.appendChild(name);
          content.appendChild(meta);
          wbCard.appendChild(checkbox);
          wbCard.appendChild(content);
          workbookGrid.appendChild(wbCard);
        });
        
        projectDiv.appendChild(workbookGrid);
        container.appendChild(projectDiv);
      });
      
      feather.replace();
      updateStats();
    }

    // Event Listeners
    document.getElementById('authForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('signInBtn');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i data-feather="loader" class="inline-block w-5 h-5 mr-2 animate-spin"></i> Connecting...';
      btn.disabled = true;
      
      server = document.getElementById('serverUrl').value;
      const site = document.getElementById('site').value;
      const tokenName = document.getElementById('tokenName').value;
      const tokenSecret = document.getElementById('tokenSecret').value;
      
      try {
        const res = await fetch('/api/signin', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({server, site, tokenName, tokenSecret})
        });
        
        const data = await res.json();
        if (data.error) {
          logMessage(`Authentication failed: ${data.error}`, 'error');
          return;
        }
        
        authToken = data.token;
        siteId = data.siteId;
        logMessage('Authentication successful', 'success');
        await fetchWorkbooks();
        
      } catch (error) {
        logMessage(`Connection error: ${error.message}`, 'error');
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
        feather.replace();
      }
    });

    async function fetchWorkbooks() {
      logMessage('Fetching workbooks...');
      try {
        const res = await fetch('/api/workbooks', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({server, siteId, token: authToken})
        });
        
        const data = await res.json();
        if (data.error) {
          logMessage(`Failed to fetch workbooks: ${data.error}`, 'error');
          return;
        }
        
        allWorkbooks = data.workbooks;
        filteredWorkbooks = [...allWorkbooks];
        
        populateFilters();
        displayWorkbooks();
        
        document.getElementById('workbookSection').classList.remove('hidden');
        document.getElementById('statsSection').classList.remove('hidden');
        
        logMessage(`Successfully loaded ${allWorkbooks.length} workbooks`, 'success');
        
      } catch (error) {
        logMessage(`Error fetching workbooks: ${error.message}`, 'error');
      }
    }

    // Filter event listeners
    ['searchInput', 'projectFilter', 'ownerFilter', 'sortBy'].forEach(id => {
      document.getElementById(id).addEventListener('input', applyFilters);
    });

    document.getElementById('selectAllButton').addEventListener('click', () => {
      document.querySelectorAll('.workbookCheckbox').forEach(cb => cb.checked = true);
      updateStats();
    });

    document.getElementById('clearAllButton').addEventListener('click', () => {
      document.querySelectorAll('.workbookCheckbox').forEach(cb => cb.checked = false);
      updateStats();
    });

    document.getElementById('refreshButton').addEventListener('click', async () => {
      const selectedIds = Array.from(document.querySelectorAll('.workbookCheckbox:checked')).map(el => el.value);
      if (selectedIds.length === 0) {
        logMessage('Please select at least one workbook to refresh', 'error');
        return;
      }
      
      const btn = document.getElementById('refreshButton');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i data-feather="loader" class="inline-block w-5 h-5 mr-2 animate-spin"></i> Refreshing...';
      btn.disabled = true;
      
      logMessage(`Starting refresh of ${selectedIds.length} workbooks...`);
      
      try {
        const res = await fetch('/api/refresh', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({server, siteId, token: authToken, workbookIds: selectedIds})
        });
        
        const results = await res.json();
        const successCount = results.filter(r => r.success).length;
        const failCount = results.length - successCount;
        
        results.forEach(result => {
          const workbook = allWorkbooks.find(wb => wb.id === result.id);
          const name = workbook ? workbook.name : result.id;
          if (result.success) {
            logMessage(`Successfully refreshed: ${name}`, 'success');
          } else {
            logMessage(`Failed to refresh ${name}: ${result.error || 'Unknown error'}`, 'error');
          }
        });
        
        logMessage(`Refresh completed: ${successCount} successful, ${failCount} failed`, successCount === results.length ? 'success' : 'error');
        
      } catch (error) {
        logMessage(`Refresh error: ${error.message}`, 'error');
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
        feather.replace();
      }
    });

    document.getElementById('exportButton').addEventListener('click', () => {
      const selectedWorkbooks = allWorkbooks.filter(wb => 
        document.querySelector(`input[value="${wb.id}"]`)?.checked
      );
      
      if (selectedWorkbooks.length === 0) {
        logMessage('No workbooks selected for export', 'error');
        return;
      }
      
      const csvContent = [
        ['Name', 'Project', 'Owner', 'Created', 'Updated', 'ID'].join(','),
        ...selectedWorkbooks.map(wb => [
          `"${wb.name}"`,
          `"${wb.project}"`,
          `"${wb.owner}"`,
          wb.createdAt ? new Date(wb.createdAt).toLocaleDateString() : '',
          wb.updatedAt ? new Date(wb.updatedAt).toLocaleDateString() : '',
          wb.id
        ].join(','))
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tableau_workbooks_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      
      logMessage(`Exported ${selectedWorkbooks.length} workbooks to CSV`, 'success');
    });

    document.getElementById('clearLogButton').addEventListener('click', () => {
      document.getElementById('log').innerHTML = '';
    });
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.json or {}
    server = data.get('server','').rstrip('/')
    site = data.get('site','')
    
    body = {
        'credentials': {
            'personalAccessTokenName': data.get('tokenName',''),
            'personalAccessTokenSecret': data.get('tokenSecret',''),
            'site': {'contentUrl': site}
        }
    }
    
    try:
        resp = requests.post(
            f"{server}/api/3.17/auth/signin", 
            json=body, 
            headers={'Content-Type':'application/json','Accept':'application/json'},
            timeout=30
        )
        
        if resp.status_code != 200:
            return jsonify(error=f"Sign-in failed ({resp.status_code}): {resp.text}"), resp.status_code
            
        creds = resp.json().get('credentials', {})
        return jsonify(
            token=creds.get('token'), 
            siteId=creds.get('site',{}).get('id')
        )
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Sign-in request failed: {e}")
        return jsonify(error=f"Connection failed: {str(e)}"), 500
    except Exception as e:
        app.logger.error(f"Sign-in error: {e}")
        return jsonify(error=f"Authentication error: {str(e)}"), 500

@app.route('/api/workbooks', methods=['POST'])
def workbooks():
    data = request.json or {}
    server = data.get('server','').rstrip('/')
    token = data.get('token','')
    siteId = data.get('siteId','')
    
    headers = {
        'X-Tableau-Auth': token, 
        'Accept': 'application/json'
    }
    
    try:
        # Fetch workbooks with pagination support
        all_workbooks = []
        page_number = 1
        page_size = 100
        
        while True:
            url = f"{server}/api/3.17/sites/{siteId}/workbooks"
            params = {
                'pageSize': page_size,
                'pageNumber': page_number,
                'fields': 'id,name,createdAt,updatedAt,project,owner'
            }
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            
            if resp.status_code != 200:
                return jsonify(error=f"Fetch workbooks failed ({resp.status_code}): {resp.text}"), resp.status_code
            
            try:
                body = resp.json()
            except ValueError:
                return jsonify(error=f"Invalid JSON response: {resp.text}"), 502
            
            workbooks_data = body.get('workbooks', {})
            workbooks = workbooks_data.get('workbook', [])
            
            if not workbooks:
                break
                
            all_workbooks.extend(workbooks)
            
            # Check if we have more pages
            pagination = body.get('pagination', {})
            total_available = int(pagination.get('totalAvailable', 0))
            
            if len(all_workbooks) >= total_available:
                break
                
            page_number += 1
        
        # Process workbooks with enhanced information
        workbook_list = []
        for wb in all_workbooks:
            workbook_info = {
                'id': wb.get('id'),
                'name': wb.get('name', 'Unknown'),
                'project': wb.get('project', {}).get('name', 'Default'),
                'owner': wb.get('owner', {}).get('name', 'Unknown'),
                'createdAt': wb.get('createdAt'),
                'updatedAt': wb.get('updatedAt'),
                'size': wb.get('size'),
                'contentUrl': wb.get('contentUrl'),
                'showTabs': wb.get('showTabs', False),
                'tags': [tag.get('label', '') for tag in wb.get('tags', {}).get('tag', [])]
            }
            workbook_list.append(workbook_info)
        
        # Sort workbooks by name for consistent ordering
        workbook_list.sort(key=lambda x: x['name'].lower())
        
        return jsonify(workbooks=workbook_list)
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Workbooks request failed: {e}")
        return jsonify(error=f"Connection failed: {str(e)}"), 500
    except Exception as e:
        app.logger.error(f"Error fetching workbooks: {e}")
        return jsonify(error=f"Failed to fetch workbooks: {str(e)}"), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    data = request.json or {}
    server = data.get('server','').rstrip('/')
    token = data.get('token','')
    siteId = data.get('siteId','')
    workbook_ids = data.get('workbookIds', [])
    
    headers = {
        'X-Tableau-Auth': token, 
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    results = []
    
    for wb_id in workbook_ids:
        try:
            # Use the extract refresh endpoint
            url = f"{server}/api/3.17/sites/{siteId}/workbooks/{wb_id}/refresh"
            
            # Prepare the refresh request body
            refresh_body = {
                "task": {
                    "extractRefresh": {
                        "type": "FullRefresh"
                    }
                }
            }
            
            resp = requests.post(
                url, 
                headers=headers, 
                json=refresh_body,
                timeout=60
            )
            
            if resp.status_code in [200, 201, 202]:
                # Parse response to get job information
                try:
                    job_info = resp.json()
                    job_id = job_info.get('job', {}).get('id')
                    results.append({
                        'id': wb_id, 
                        'success': True, 
                        'jobId': job_id,
                        'message': 'Refresh job started successfully'
                    })
                except:
                    results.append({
                        'id': wb_id, 
                        'success': True,
                        'message': 'Refresh initiated successfully'
                    })
            else:
                error_msg = f"HTTP {resp.status_code}"
                try:
                    error_response = resp.json()
                    if 'error' in error_response:
                        error_msg = error_response['error'].get('summary', error_msg)
                except:
                    error_msg = resp.text[:200] if resp.text else error_msg
                    
                results.append({
                    'id': wb_id, 
                    'success': False, 
                    'error': error_msg
                })
                
        except requests.exceptions.Timeout:
            results.append({
                'id': wb_id, 
                'success': False, 
                'error': 'Request timeout - refresh may still be processing'
            })
        except requests.exceptions.RequestException as e:
            results.append({
                'id': wb_id, 
                'success': False, 
                'error': f'Connection error: {str(e)}'
            })
        except Exception as e:
            app.logger.error(f"Error refreshing workbook {wb_id}: {e}")
            results.append({
                'id': wb_id, 
                'success': False, 
                'error': f'Unexpected error: {str(e)}'
            })
    
    return jsonify(results)

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a refresh job"""
    data = request.args
    server = data.get('server','').rstrip('/')
    token = data.get('token','')
    siteId = data.get('siteId','')
    
    headers = {
        'X-Tableau-Auth': token, 
        'Accept': 'application/json'
    }
    
    try:
        url = f"{server}/api/3.17/sites/{siteId}/jobs/{job_id}"
        resp = requests.get(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            return jsonify(resp.json())
        else:
            return jsonify(error=f"Failed to get job status ({resp.status_code}): {resp.text}"), resp.status_code
            
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Job status request failed: {e}")
        return jsonify(error=f"Connection failed: {str(e)}"), 500
    except Exception as e:
        app.logger.error(f"Error checking job status: {e}")
        return jsonify(error=f"Failed to get job status: {str(e)}"), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

# This is required for Vercel deployment
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True) 