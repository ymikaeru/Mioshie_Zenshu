/**
 * Showa Year Converter
 * Converts Japanese Showa era years to Western calendar years
 * Showa 1 (昭和1年) = 1926, so Showa N = 1925 + N
 */
(function () {
    'use strict';

    // Map fullwidth digits to halfwidth
    const fullwidthToHalfwidth = {
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
    };

    function convertFullwidthToNumber(str) {
        let result = '';
        for (let char of str) {
            result += fullwidthToHalfwidth[char] || char;
        }
        return parseInt(result, 10);
    }

    function convertShowaToWestern(showaYear) {
        return 1925 + showaYear;
    }

    function processHeaders() {
        // Only target the innermost strong element inside font[size="4"]
        // This prevents double processing
        const elements = document.querySelectorAll('font[size="4"] > strong');

        elements.forEach(el => {
            // Skip if already converted
            if (el.dataset.showaConverted === 'true') return;

            const text = el.textContent || el.innerText;

            // Ensure we don't match if already converted (has parentheses with year)
            if (text.includes('(19') || text.includes('(20')) return;

            // Match patterns like 昭和２４年 or 昭和24年 (with fullwidth or halfwidth numbers)
            // The pattern captures the year number
            const showaPattern = /昭和([０-９0-9]+)年/;
            const match = text.match(showaPattern);

            if (match) {
                const showaYear = convertFullwidthToNumber(match[1]);
                const westernYear = convertShowaToWestern(showaYear);

                // Add Western year in parentheses after the matched pattern
                const newText = text.replace(
                    showaPattern,
                    `昭和${match[1]}年 (${westernYear})`
                );

                el.textContent = newText;
                el.dataset.showaConverted = 'true';
            }
        });
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', processHeaders);
    } else {
        processHeaders();
    }
})();
