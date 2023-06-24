import { ConnectKitButton } from "connectkit";
import { Caisson } from "./Caisson";
import { CustomButton } from "./CustomButton";
import styled from "styled-components";

interface HeaderProps {
  redirectTo: string;
}

export const Header: React.FC<HeaderProps> = ({ redirectTo }) => {
  return (
    <div className="flex justify-between items-center p-4">
      <Caisson />
      <div className="flex items-center gap-8">
        <CustomButton redirectTo={redirectTo} />
      </div>
    </div>
  );
};
