import { useLang } from "./index";

export default function useTranslation() {
  const { t } = useLang();
  return t;
}
