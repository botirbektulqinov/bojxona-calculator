// Bojxona Kalkulyatori - Frontend JavaScript

const API_BASE = '/api/v1';

// State
let selectedTnved = null;
let tnvedName = '';
let searchTimeout = null;

// DOM tayyor bo'lganda
document.addEventListener('DOMContentLoaded', function() {
    setupTnvedSearch();
    setupCountryInfo();
    setupFormSubmit();
    loadCurrencyRates();
});
function setupTnvedSearch() {
    const tnvedInput = document.getElementById('tnved-code');
    const resultsDiv = document.getElementById('tnved-results');
    
    if (!tnvedInput || !resultsDiv) return;
    
    // Input event - yozish vaqtida qidirish
    tnvedInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Oldingi timeout ni bekor qilish
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // 2 belgidan kam bo'lsa - yashirish
        if (query.length < 2) {
            resultsDiv.classList.add('hidden');
            resultsDiv.innerHTML = '';
            return;
        }
        
        // 300ms kutib qidirish (debounce)
        searchTimeout = setTimeout(() => {
            searchTnved(query);
        }, 300);
    });
    
    // Input ga fokus bo'lganda
    tnvedInput.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= 2) {
            searchTnved(query);
        }
    });
    
    // Tashqariga bosganda yashirish
    document.addEventListener('click', function(e) {
        if (!tnvedInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.classList.add('hidden');
        }
    });
}

async function searchTnved(query) {
    const resultsDiv = document.getElementById('tnved-results');
    
    try {
        const response = await fetch(`${API_BASE}/tnved/search?q=${encodeURIComponent(query)}&limit=10`);
        
        if (!response.ok) {
            throw new Error('Qidiruv xatosi');
        }
        
        const results = await response.json();
        displayTnvedResults(results);
        
    } catch (error) {
        console.error('TNVED qidiruv xatosi:', error);
        resultsDiv.innerHTML = `
            <div class="p-3 text-red-600 text-sm">
                Qidiruvda xatolik yuz berdi
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }
}

function displayTnvedResults(results) {
    const resultsDiv = document.getElementById('tnved-results');
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="p-3 text-gray-500 text-sm">
                Natija topilmadi. Boshqa kod yoki kalit so'z bilan qidiring.
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        return;
    }
    
    resultsDiv.innerHTML = results.map(item => `
        <div class="tnved-item p-3 hover:bg-indigo-50 cursor-pointer border-b border-gray-100 last:border-0 transition-colors"
             onclick="selectTnved('${item.code}', '${(item.description || '').replace(/'/g, "\\'")}')">
            <div class="flex justify-between items-start gap-2">
                <span class="font-mono text-indigo-600 font-semibold text-sm">${item.code}</span>
            </div>
            <div class="text-sm text-gray-600 mt-1 line-clamp-2">${item.description || 'Nomi ko\'rsatilmagan'}</div>
        </div>
    `).join('');
    
    resultsDiv.classList.remove('hidden');
}

function selectTnved(code, name) {
    const tnvedInput = document.getElementById('tnved-code');
    const resultsDiv = document.getElementById('tnved-results');
    const productNameSpan = document.getElementById('product-name');
    
    selectedTnved = code;
    tnvedName = name;
    tnvedInput.value = code;
    
    if (productNameSpan) {
        productNameSpan.textContent = name || '';
        productNameSpan.parentElement.classList.toggle('hidden', !name);
    }
    
    resultsDiv.classList.add('hidden');
}

// ============================================
// Mamlakat Info
// ============================================
function setupCountryInfo() {
    const countrySelect = document.getElementById('country');
    const countryInfo = document.getElementById('country-info');
    const certificateSection = document.getElementById('certificate-section');
    
    if (!countrySelect) return;
    
    // MDH (erkin savdo) mamlakatlar
    const freeTradeCountries = ['RU', 'KZ', 'KG', 'TJ', 'BY', 'AM', 'MD', 'UA', 'AZ', 'GE'];
    
    countrySelect.addEventListener('change', function() {
        const code = this.value;
        
        if (countryInfo) {
            if (code === 'XX') {
                countryInfo.textContent = '⚠️ Noma\'lum mamlakat uchun 2x boj stavkasi qo\'llanadi';
                countryInfo.className = 'mt-1 text-xs text-orange-600';
            } else if (freeTradeCountries.includes(code)) {
                countryInfo.textContent = '✅ Erkin savdo zonasi - ST-1 sertifikati bilan 0% boj';
                countryInfo.className = 'mt-1 text-xs text-green-600';
            } else {
                countryInfo.textContent = '';
            }
        }
        
        // ST-1 checkbox ni ko'rsatish/yashirish
        if (certificateSection) {
            certificateSection.classList.toggle('hidden', !freeTradeCountries.includes(code));
        }
    });
}

// ============================================
// Valyuta kurslari
// ============================================
async function loadCurrencyRates() {
    try {
        const response = await fetch(`${API_BASE}/currency/rate/USD`);
        if (response.ok) {
            const data = await response.json();
            const rateSpan = document.getElementById('usd-rate');
            if (rateSpan) {
                rateSpan.textContent = `1 USD = ${Number(data.rate).toLocaleString('uz-UZ')} so'm`;
            }
        }
    } catch (error) {
        console.error('Valyuta kursi xatosi:', error);
    }
}

// ============================================
// Form Submit - Hisoblash
// ============================================
function setupFormSubmit() {
    const form = document.getElementById('calc-form');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await calculateCustoms();
    });
}

async function calculateCustoms() {
    // Input qiymatlarni olish
    const tnvedCode = document.getElementById('tnved-code')?.value?.trim();
    const price = parseFloat(document.getElementById('price')?.value) || 0;
    const currency = document.getElementById('currency')?.value || 'USD';
    const country = document.getElementById('country')?.value || 'XX';
    const hasCertificate = document.getElementById('has-certificate')?.checked || false;
    const delivery = parseFloat(document.getElementById('delivery')?.value) || 0;
    const insurance = parseFloat(document.getElementById('insurance')?.value) || 0;
    const engineVolume = parseInt(document.getElementById('engine-volume')?.value) || null;
    const weight = parseFloat(document.getElementById('weight')?.value) || 1; // Default 1 kg
    
    // Validatsiya
    if (!tnvedCode || tnvedCode.length < 2) {
        showError('TN VED kodini kiriting (kamida 2 raqam)');
        return;
    }
    
    if (price <= 0) {
        showError('Tovar narxini kiriting');
        return;
    }
    
    // Loading ko'rsatish
    showLoading(true);
    hideResults();
    
    // API so'rov
    const requestData = {
        code: tnvedCode,
        price: price,
        currency: currency,
        weight: weight,
        country_origin: country,
        has_certificate: hasCertificate,
        delivery_cost: delivery,
        insurance_cost: insurance,
        engine_volume: engineVolume
    };
    
    try {
        const response = await fetch(`${API_BASE}/calculator/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            // API xatosi
            let errorMsg = 'Hisoblashda xatolik yuz berdi';
            if (data.detail) {
                if (typeof data.detail === 'string') {
                    errorMsg = data.detail;
                } else if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(d => d.msg || d).join(', ');
                }
            }
            showError(errorMsg);
        }
        
    } catch (error) {
        console.error('Hisoblash xatosi:', error);
        showError('Server bilan bog\'lanishda xatolik');
    } finally {
        showLoading(false);
    }
}

// ============================================
// Natijalarni ko'rsatish
// ============================================
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const emptyState = document.getElementById('empty-state');
    if (!resultsDiv) return;
    
    // Empty state ni yashirish
    if (emptyState) {
        emptyState.classList.add('hidden');
    }
    
    // Duty type badge ranglari
    const dutyTypeBadges = {
        'standard': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Standart tarif' },
        'free_trade': { bg: 'bg-green-100', text: 'text-green-800', label: 'Erkin savdo (0%)' },
        'cis_with_certificate': { bg: 'bg-green-100', text: 'text-green-800', label: 'MDH + ST-1 (0%)' },
        'unknown_country': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Noma\'lum mamlakat (2x)' }
    };
    
    const badge = dutyTypeBadges[data.duty_rate_type] || dutyTypeBadges['standard'];
    
    let html = '';
    
    // Ogohlantirishlar
    if (data.warnings && data.warnings.length > 0) {
        html += `
            <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                <div class="flex">
                    <svg class="h-5 w-5 text-amber-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                    <div class="text-sm text-amber-800">
                        ${data.warnings.map(w => `<p>${w}</p>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Tarif turi badge
    html += `
        <div class="mb-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${badge.bg} ${badge.text}">
                ${badge.label}
            </span>
        </div>
    `;
    
    // Bojxona qiymati
    html += `
        <div class="bg-gray-50 rounded-lg p-4 mb-4">
            <div class="text-sm text-gray-500 mb-1">Bojxona qiymati (TS)</div>
            <div class="text-2xl font-bold text-gray-900">
                ${formatMoney(data.customs_value_uzs)} so'm
            </div>
            <div class="text-sm text-gray-500 mt-1">
                ≈ ${formatMoney(data.customs_value_usd)} USD
            </div>
        </div>
    `;
    
    // To'lovlar jadvali
    if (data.payments && data.payments.length > 0) {
        html += `
            <div class="mb-4">
                <h3 class="text-sm font-semibold text-gray-900 mb-2">To'lovlar tafsiloti</h3>
                <div class="border border-gray-200 rounded-lg overflow-hidden">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">To'lov turi</th>
                                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Stavka</th>
                                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Summa</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${data.payments.map(p => `
                                <tr>
                                    <td class="px-3 py-2 text-sm text-gray-900">${p.name_uz || p.name}</td>
                                    <td class="px-3 py-2 text-sm text-gray-500 text-right">
                                        ${p.rate !== null && p.rate !== undefined ? 
                                            (p.rate_type === 'percent' ? `${p.rate}%` : formatMoney(p.rate)) : 
                                            '-'}
                                    </td>
                                    <td class="px-3 py-2 text-sm font-medium text-gray-900 text-right">
                                        ${formatMoney(p.amount)} so'm
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    // Jami summa
    html += `
        <div class="bg-indigo-600 rounded-lg p-4 text-white">
            <div class="flex justify-between items-center">
                <div>
                    <div class="text-indigo-200 text-sm">Jami to'lovlar</div>
                    <div class="text-2xl font-bold mt-1">${formatMoney(data.total_uzs)} so'm</div>
                </div>
                <div class="text-right">
                    <div class="text-indigo-200 text-sm">USD da</div>
                    <div class="text-xl font-semibold mt-1">≈ $${formatMoney(data.total_usd)}</div>
                </div>
            </div>
            ${data.effective_rate_percent ? `
                <div class="mt-3 pt-3 border-t border-indigo-500 text-sm text-indigo-200">
                    Effektiv stavka: ${data.effective_rate_percent.toFixed(2)}% (tovar qiymatidan)
                </div>
            ` : ''}
        </div>
    `;
    
    // Valyuta kursi
    if (data.exchange_rate) {
        html += `
            <div class="mt-3 text-center text-xs text-gray-500">
                Kurs: 1 USD = ${formatMoney(data.exchange_rate)} so'm (CBU)
            </div>
        `;
    }
    
    // Data source info
    if (data.data_source || data.sync_info) {
        html += `
            <div class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex items-center justify-center space-x-2 text-xs text-gray-500">
                    <svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                    <span>${data.sync_info || 'Ma\'lumotlar ' + data.data_source + ' dan'}</span>
                </div>
            </div>
        `;
    }
    
    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('hidden');
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================
// Yordamchi funksiyalar
// ============================================
function formatMoney(amount) {
    if (amount === null || amount === undefined) return '0';
    return Number(amount).toLocaleString('uz-UZ', { 
        minimumFractionDigits: 0,
        maximumFractionDigits: 2 
    });
}

function showLoading(show) {
    const btn = document.getElementById('submit-btn');
    if (!btn) return;
    
    if (show) {
        btn.disabled = true;
        btn.innerHTML = `
            <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Hisoblanmoqda...</span>
        `;
    } else {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            <span>Hisoblash</span>
        `;
    }
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
                <svg class="h-5 w-5 text-red-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>
                <span class="text-red-800 text-sm">${message}</span>
            </div>
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

function hideResults() {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.classList.add('hidden');
    }
}
