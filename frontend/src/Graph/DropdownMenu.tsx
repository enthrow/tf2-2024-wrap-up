import React, { useState, useEffect, useRef } from "react";

interface DropdownMenuProps {
  id: string; // The dynamic part of the URL
}

const DropdownMenu: React.FC<DropdownMenuProps> = ({ id }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const links = [
    { label: "Steam", baseUrl: "https://steamcommunity.com/profiles/" },
    { label: "logs.tf", baseUrl: "https://logs.tf/profile/" },
    { label: "demos.tf", baseUrl: "https://demos.tf/profiles/" },
    { label: "trends.tf", baseUrl: "https://trends.tf/player/76561198138221795/" },
    { label: "UGC", baseUrl: "https://www.ugcleague.com/players_page_alt.cfm?player_id=" },
    { label: "RGL", baseUrl: "https://rgl.gg/Public/PlayerProfile?p=" },
    { label: "ETF2L", baseUrl: "https://etf2l.org/search/" },
    { label: "UGC", baseUrl: "https://www.ugcleague.com/players_page_alt.cfm?player_id=" },
    { label: "ozfortress", baseUrl: "https://ozfortress.com/users/steam_id/" },
    { label: "TF2Center", baseUrl: "https://tf2center.com/profile/" },
  ];

  const toggleDropdown = () => setIsOpen((prev) => !prev);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="dropdown-container" ref={dropdownRef}>
      {/* Dropdown Trigger */}
      <span className="dropdown-trigger" onClick={toggleDropdown}>
        ▼
      </span>

      {/* Dropdown Menu */}
      {isOpen && (
        <ul className="dropdown-menu">
          {links.map((link, index) => (
            <li key={index}>
              <a
                href={`${link.baseUrl}${id}`} // Append the dynamic ID
                target="_blank"
                rel="noopener noreferrer"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DropdownMenu;
