package br.ufg.inf.integrador.processor;

import br.ufg.inf.integrador.model.EstudanteCanonico;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Processador especializado para transformações da entidade Estudante
 * 
 * Implementa o padrão Message Translator específico para:
 * - Estudante (SGA/ORM) → Usuario (SB/ODM)
 * - Estudante (SGA/ORM) → EstudanteCanonico (Modelo Canônico)
 * 
 * Responsabilidades:
 * - Divisão de nome completo em prenome/sobrenome
 * - Mapeamento de status entre sistemas
 * - Criação de dados canônicos normalizados
 */
public class EstudanteProcessor {
    
    private static final Logger logger = LoggerFactory.getLogger(EstudanteProcessor.class);
    private final Gson gson = new Gson();
    
    /**
     * Transforma os dados JSON de um estudante em um objeto Usuario (compatível com o SB).
     * 
     * Transformações realizadas:
     * - nome_completo → prenome + sobrenome (divisão no primeiro espaço)
     * - status_emprestimo_livros → situacao_matricula (mapeamento de valores)
     * - Campos específicos do SGA são omitidos (data_nascimento, matricula)
     * 
     * @param dadosJson JSON contendo os dados do estudante do SGA
     * @return JSON do objeto Usuario serializado, ou null em caso de erro
     */
    public String estudanteParaUsuario(String dadosJson) {
        try {
            logger.debug("🔄 Transformando Estudante → Usuario");
            logger.debug("📋 Dados de entrada: {}", dadosJson);
            
            // Parse dos dados JSON do estudante
            JsonObject estudanteJson = JsonParser.parseString(dadosJson).getAsJsonObject();
            
            // Extrair nome completo e dividir em prenome/sobrenome
            String nomeCompleto = estudanteJson.has("nome_completo") ? 
                estudanteJson.get("nome_completo").getAsString() : "";
            
            String[] partesNome = extrairPrenomeESobrenome(nomeCompleto);
            String prenome = partesNome[0];
            String sobrenome = partesNome[1];
            
            // Mapear status de empréstimo para situação de matrícula
            String statusEmprestimo = estudanteJson.has("status_emprestimo_livros") ?
                estudanteJson.get("status_emprestimo_livros").getAsString() : "QUITADO";
            String situacaoMatricula = mapearStatusParaSituacao(statusEmprestimo);
            
            // Criar objeto Usuario para o SB
            Map<String, String> usuario = new HashMap<>();
            usuario.put("prenome", prenome);
            usuario.put("sobrenome", sobrenome);
            usuario.put("situacao_matricula", situacaoMatricula);
            
            String usuarioJson = gson.toJson(usuario);
            
            logger.info("✅ Transformação concluída:");
            logger.info("   📝 Nome: {} {} → Prenome: '{}', Sobrenome: '{}'", 
                       nomeCompleto, "", prenome, sobrenome);
            logger.info("   🎯 Status: {} → {}", statusEmprestimo, situacaoMatricula);
            logger.debug("📋 Dados de saída: {}", usuarioJson);
            
            return usuarioJson;
            
        } catch (Exception e) {
            logger.error("❌ Erro ao transformar estudante para usuário: {}", e.getMessage(), e);
            return null;
        }
    }
    
    /**
     * Transforma os dados JSON de um estudante em um objeto EstudanteCanonico.
     * 
     * @param dadosJson JSON contendo os dados do estudante
     * @param idCanonico ID canônico a ser atribuído ao estudante
     * @return Objeto EstudanteCanonico populado, ou null em caso de erro
     */
    public EstudanteCanonico estudanteParaEstudanteCanonico(String dadosJson, String idCanonico) {
        try {
            logger.debug("🔄 Criando EstudanteCanonico com ID: {}", idCanonico);
            
            JsonObject estudanteJson = JsonParser.parseString(dadosJson).getAsJsonObject();
            
            // Extrair campos do JSON
            String nomeCompleto = estudanteJson.has("nome_completo") ? 
                estudanteJson.get("nome_completo").getAsString() : "";
            String dataDeNascimento = estudanteJson.has("data_de_nascimento") ?
                estudanteJson.get("data_de_nascimento").getAsString() : "";
            String matricula = estudanteJson.has("matricula") ?
                estudanteJson.get("matricula").getAsString() : "";
            String statusEmprestimo = estudanteJson.has("status_emprestimo_livros") ?
                estudanteJson.get("status_emprestimo_livros").getAsString() : "QUITADO";
            
            // Dividir nome em prenome/sobrenome
            String[] partesNome = extrairPrenomeESobrenome(nomeCompleto);
            
            // Criar objeto canônico
            EstudanteCanonico canonico = new EstudanteCanonico();
            canonico.setIdCanonico(idCanonico);
            canonico.setPrenome(partesNome[0]);
            canonico.setSobrenome(partesNome[1]);
            canonico.setNomeCompleto(nomeCompleto);
            canonico.setDataDeNascimento(dataDeNascimento);
            canonico.setMatricula(matricula);
            canonico.setStatusAcademico("ATIVO"); // Status derivado
            canonico.setStatusBiblioteca(statusEmprestimo);
            
            logger.info("🏛️ EstudanteCanonico criado: {}", canonico);
            
            return canonico;
            
        } catch (Exception e) {
            logger.error("❌ Erro ao criar EstudanteCanonico: {}", e.getMessage(), e);
            return null;
        }
    }
    
    /**
     * Sobrecarga que gera automaticamente um ID canônico
     */
    public EstudanteCanonico estudanteParaEstudanteCanonico(String dadosJson) {
        String idCanonico = UUID.randomUUID().toString();
        return estudanteParaEstudanteCanonico(dadosJson, idCanonico);
    }
    
    /**
     * Extrai o nome completo dos dados JSON
     */
    public String extrairNomeCompleto(String dadosJson) {
        try {
            JsonObject json = JsonParser.parseString(dadosJson).getAsJsonObject();
            return json.has("nome_completo") ? json.get("nome_completo").getAsString() : "";
        } catch (Exception e) {
            logger.error("❌ Erro ao extrair nome completo: {}", e.getMessage());
            return "";
        }
    }
    
    /**
     * Divide o nome completo em prenome e sobrenome
     * 
     * Regras:
     * - Primeiro token = prenome
     * - Resto = sobrenome (se existir)
     * - Se nome vazio, retorna strings vazias
     * 
     * @param nomeCompleto Nome completo a ser dividido
     * @return Array com [prenome, sobrenome]
     */
    public String[] extrairPrenomeESobrenome(String nomeCompleto) {
        if (nomeCompleto == null || nomeCompleto.trim().isEmpty()) {
            return new String[]{"", ""};
        }
        
        String[] partes = nomeCompleto.trim().split("\\s+", 2);
        String prenome = partes[0];
        String sobrenome = partes.length > 1 ? partes[1] : "";
        
        logger.debug("👤 Nome dividido: '{}' → Prenome: '{}', Sobrenome: '{}'", 
                    nomeCompleto, prenome, sobrenome);
        
        return new String[]{prenome, sobrenome};
    }
    
    /**
     * Mapeia status de empréstimo do SGA para situação de matrícula do SB
     * 
     * Regras de mapeamento:
     * - "QUITADO" → "ATIVO" (pode usar biblioteca)
     * - "EM_ABERTO" → "INATIVO" (bloqueado na biblioteca)
     * - Outros valores → "ATIVO" (padrão permissivo)
     */
    private String mapearStatusParaSituacao(String statusEmprestimo) {
        if (statusEmprestimo == null) {
            return "ATIVO";
        }
        
        switch (statusEmprestimo.toUpperCase()) {
            case "QUITADO":
                return "ATIVO";
            case "EM_ABERTO":
                return "INATIVO";
            default:
                logger.warn("⚠️ Status de empréstimo desconhecido: {}. Usando ATIVO como padrão.", 
                           statusEmprestimo);
                return "ATIVO";
        }
    }
}